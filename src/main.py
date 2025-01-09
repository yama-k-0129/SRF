# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

from .file_io.config_manager import ConfigManager
from .file_io.gis_reader import GISDataReader
from .file_io.file_utils import read_rainfall_data
from .calculators.flood_arrival_calculator import FloodArrivalCalculator
from .calculators.rational_method_calculator import RationalMethodCalculator
from .utils.geo_utils import find_nearest_point_data
import subprocess
from pathlib import Path
import pandas as pd
import os
import numpy as np

class AnalysisPoint:
    """解析地点を表すクラス"""
    def __init__(self, lon, lat, link_id):
        self.lon = lon
        self.lat = lat
        self.link_id = link_id
        self.output_files = {}

def read_analysis_points(file_path):
    """
    解析地点ファイルを読み込む
    
    Parameters:
    -----------
    file_path : str
        解析地点ファイルのパス
    
    Returns:
    --------
    list[AnalysisPoint]
        解析地点のリスト
    """
    try:
        points_df = pd.read_csv(file_path)
        required_columns = ['target_lon', 'target_lat', 'target_linkid']
        if not all(col in points_df.columns for col in required_columns):
            raise ValueError(f"必要なカラム {required_columns} が見つかりません")
        
        return [
            AnalysisPoint(row['target_lon'], row['target_lat'], row['target_linkid'])
            for _, row in points_df.iterrows()
        ]
    except Exception as e:
        print(f"解析地点ファイルの読み込みエラー: {e}")
        raise

def create_output_path_for_point(point_id):
    """
    extract_basin.exeの出力ファイルパスを生成する
    
    Parameters:
    -----------
    point_id : Union[str, int, float]
        解析地点のID
    
    Returns:
    --------
    tuple[dict, dict]
        (元のファイルパス, リネーム後のファイルパス)
    """
    point_id_str = str(int(float(point_id)))
    base_paths = {
        'distance': 'log/dir.txt_distance.txt',
        'elevation': 'log/dem.txt_extracted.txt',
        'landuse': 'log/landuse.txt_extracted.txt',
        'basin': 'log/dir.txt_basin.txt',
        'timedelay': 'log/flood_arrival_time.asc',
        'flow': 'out/asuwatyuryu_flow2.csv'
    }
    
    # extract_basin.exeが生成したファイルを後で適切な名前にリネーム
    renamed_paths = {}
    for key, base_path in base_paths.items():
        path = Path(base_path)
        new_path = path.parent / f"{path.stem}_{point_id_str}{path.suffix}"
        renamed_paths[key] = str(new_path)
    
    return base_paths, renamed_paths

def rename_output_files(base_paths, renamed_paths):
    """
    extract_basin.exeが生成したファイルを解析地点ごとの名前にリネームする
    
    Parameters:
    -----------
    base_paths : dict
        元のファイルパス
    renamed_paths : dict
        リネーム後のファイルパス
    """
    for key in base_paths.keys():
        if Path(base_paths[key]).exists():
            # 既存のリネーム先ファイルがあれば削除
            if Path(renamed_paths[key]).exists():
                Path(renamed_paths[key]).unlink()
            # リネーム実行
            Path(base_paths[key]).rename(renamed_paths[key])

def check_output_file_exists(filepath: str, description: str = "") -> None:
    """
    出力ファイルの存在を確認する
    
    Parameters:
    -----------
    filepath : str
        確認するファイルパス
    description : str
        ファイルの説明（エラーメッセージ用）
    
    Raises:
    -------
    RuntimeError
        ファイルが存在しない場合
    """
    if not Path(filepath).exists():
        error_msg = f"Output file not created: {filepath}"
        if description:
            error_msg += f" ({description})"
        raise RuntimeError(error_msg)

def prepare_output_directories():
    """出力ディレクトリを作成する"""
    required_dirs = ['log', 'out']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

def merge_flow_results(points, output_path, dtq):
    """
    全地点の流量計算結果をマージする
    
    Parameters:
    -----------
    points : list[AnalysisPoint]
        解析地点のリスト
    output_path : str
        出力ファイルパス
    dtq : float
        時間間隔（秒）
    """
    dfs = []
    for point in points:
        df = pd.read_csv(point.output_files['flow'])
        # IDから小数点を削除して整数に変換
        point_id = str(int(float(point.link_id)))
        # Flow(m3/s) カラムの名前を整数のIDに基づいて変更
        df = df.rename(columns={'Flow(m3/s)': f'flow_{point_id}'})
        dfs.append(df)
    
    # 最も長いタイムステップを持つデータフレームを見つける
    max_time = max(df['Time(s)'].max() for df in dfs)
    # 全タイムステップを生成（dtqの間隔で）
    full_time_range = pd.DataFrame({'Time(s)': np.arange(0, max_time + dtq, dtq)})
    
    # 最初のデータフレームをベースに他のデータフレームをマージ
    result = full_time_range
    for df in dfs:
        # 外部結合（outer）を使用し、NaNを0.0で埋める
        result = pd.merge(result, df, on='Time(s)', how='outer').fillna(0.0)
    
    # Time(s)でソート
    result = result.sort_values('Time(s)')
    
    result.to_csv(output_path, index=False)

def main():
    """メイン処理"""
    # プロジェクトルートパスの取得
    project_root = Path(__file__).parent.parent
    
    # 設定ファイルのパスを構築
    config_path = project_root / 'config' / 'config.yml'
    
    # ConfigManagerの初期化
    config = ConfigManager(str(config_path))
    paths = config.file_paths
    params = config.parameters
    
    # 出力ディレクトリの準備
    prepare_output_directories()
    
    # 解析地点の読み込み
    analysis_points = read_analysis_points(config.analysis_points['input_file'])
    
    # GISDataReaderのインスタンス化
    reader = GISDataReader()
    
    # 各解析地点に対して処理を実行
    for point in analysis_points:
        print(f"Processing point {point.link_id} ({point.lon}, {point.lat})")
        
        # 出力ファイルパスの生成
        base_paths, renamed_paths = create_output_path_for_point(point.link_id)
        point.output_files = renamed_paths
        
        # upgファイルの確認と読み込み
        if paths.get('upg_file') is None:
            print("alert no upgfile")
        else:
            upg_data, upg_x_coords, upg_y_coords = reader.read_gis_file(paths['upg_file'])
        
        # 流向データの読み込み
        dir_data, dir_x_coords, dir_y_coords = reader.read_gis_file(paths['dir_file'])
        
        # 最近傍点の検索と閾値判定
        nearest_x, nearest_y, value, is_above, num_x, num_y = find_nearest_point_data(
            upg_x_coords,
            upg_y_coords,
            upg_data,
            point.lon,
            point.lat,
            reader.metadata.xllcorner,
            reader.metadata.yllcorner,
            reader.metadata.cellsize,
            params['threshold'],
            reader.metadata
        )
        
        if not is_above:
            print(f"error : not river for point {point.link_id}")
            print(f"指定座標: ({point.lon}, {point.lat})")
            print(f"最近傍の格子点: ({nearest_x:.4f}, {nearest_y:.4f})")
            print(f"データ値: {value:.2f}")
            print(f"閾値超過: {is_above}")
            continue
        
        # 流域抽出
        result = subprocess.run([
            paths['extract_basin_exe'],
            paths['dir_file'],
            str(num_x),
            str(num_y),
            paths['dem_file'],
            paths['landuse_file']
        ], text=True)
        
        if result.returncode != 0:
            print(f"Error in extract_basin.exe: {result.stderr}")
            continue
            
        # 出力ファイルのリネーム
        rename_output_files(base_paths, renamed_paths)
        
        # extract_basin.exeが生成するファイルの存在確認
        extract_basin_outputs = ['distance', 'elevation', 'landuse', 'basin']
        for file_type in extract_basin_outputs:
            filepath = point.output_files[file_type]
            check_output_file_exists(filepath, f"after extract_basin.exe for point {point.link_id}")
        
        # 洪水到達時間の計算
        flood_calculator = FloodArrivalCalculator(reader)
        flood_calculator.process_and_save(
            point.output_files['distance'],
            point.output_files['elevation'],
            point.output_files['timedelay']
        )
        
        # 合成合理式による流量計算
        rational_calculator = RationalMethodCalculator(reader)
        rational_calculator.load_data(
            point.output_files['timedelay'],
            point.output_files['landuse']
        )
        
        # 雨量データの読み込みと流量計算
        rainfall_data = read_rainfall_data(paths['rainfall_file'])
        flow_results = rational_calculator.calculate_flow(
            rainfall_data,
            params['dtq']
        )
        
        # 結果の出力
        rational_calculator.export_results(
            flow_results,
            point.output_files['flow']
        )
    
    # 全地点の結果をマージして出力
    merge_flow_results(analysis_points, paths['flow_results_file'], params['dtq'])


if __name__ == "__main__":
    main()