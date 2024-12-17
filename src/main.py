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
    
    # GISDataReaderのインスタンス化
    reader = GISDataReader()
    
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
        params['target_lon'],
        params['target_lat'],
        reader.metadata.xllcorner,
        reader.metadata.yllcorner,
        reader.metadata.cellsize,
        params['threshold'],
        reader.metadata  # 追加
    )
    
    if not is_above:
        print("error : not river")
        print(f"指定座標: ({params['target_lon']}, {params['target_lat']})")
        print(f"最近傍の格子点: ({nearest_x:.4f}, {nearest_y:.4f})")
        print(f"データ値: {value:.2f}")
        print(f"閾値超過: {is_above}")
    
    # 流域抽出
    result = subprocess.run([
        paths['extract_basin_exe'],
        paths['dir_file'],
        str(num_x),
        str(num_y),
        paths['dem_file'],
        paths['landuse_file']
    ], text=True)
    
    # 洪水到達時間の計算
    flood_calculator = FloodArrivalCalculator(reader)
    flood_calculator.process_and_save(
        paths['distance_file'],
        paths['elevation_file'],
        paths['timedelay_file']
    )
    
    # 合成合理式による流量計算
    rational_calculator = RationalMethodCalculator(reader)
    rational_calculator.load_data(
        paths['timedelay_file'],
        paths['landuse_extracted_file']
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
        paths['flow_results_file']
    )


if __name__ == "__main__":
    main()