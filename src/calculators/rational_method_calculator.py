# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

import numpy as np
from typing import Dict
from ..file_io.gis_reader import GISDataReader
from .cell_size_calculator import CellSizeCalculator

class RationalMethodCalculator:
    """合成合理式を使用して流量を計算するクラス"""
    
    def __init__(self, gis_reader: GISDataReader):
        """
        Parameters:
        -----------
        gis_reader : GISDataReader
            GISデータを読み込むためのリーダークラスのインスタンス
        """
        self.gis_reader = gis_reader
        self.arrival_time = None
        self.landuse = None
        self.cell_calculator = CellSizeCalculator()
        self.dx = None
        self.dy = None
        self.cell_area = None
        # 土地利用別の流出係数
        # 参考：中小河川計画検討会, 中小河川計画の手引き(案) H11.9 p.60
        # データ参考：旭一岳・清水康行, RRIモデルを例とした流域治水推進に向けたデータ・解析ツールの整備・公開について, 河川技術論文集27, 2021.6
        # https://www.jstage.jst.go.jp/article/river/27/0/27_PS3-22/_pdf
        self.runoff_coefficients = {
            1: 0.7,  # 水田
            2: 0.6,  # 畑地
            3: 0.7,  # 山地
            4: 0.8,  # 都市
            5: 1.0   # 水域
        }
    
    def load_data(self, arrival_time_file: str, landuse_file: str):
        """
        到達時間と土地利用データを読み込み、セルサイズを計算
        
        Parameters:
        -----------
        arrival_time_file : str
            到達時間データのファイルパス
        landuse_file : str
            土地利用データのファイルパス
        """
        # 到達時間データの読み込み
        self.arrival_time, _, _ = self.gis_reader.read_gis_file(arrival_time_file)
        
        # 土地利用データの読み込み
        self.landuse, _, _ = self.gis_reader.read_gis_file(
            landuse_file, 
            expected_metadata=self.gis_reader.metadata
        )
        
        # セルサイズの計算
        self.dx, self.dy, _, self.cell_area = self.cell_calculator.calculate_cell_size(
            self.gis_reader.metadata
        )
        
        print(f"Calculated cell sizes:")
        print(f"dx [m]: {self.dx:.2f}")
        print(f"dy [m]: {self.dy:.2f}")
        print(f"cell area [m2]: {self.cell_area:.2f}")

    def get_runoff_coefficient(self, landuse_type: int) -> float:
        """
        土地利用種別から流出係数を取得
        
        Parameters:
        -----------
        landuse_type : int
            土地利用種別
            
        Returns:
        --------
        float
            流出係数
        """
        return self.runoff_coefficients.get(landuse_type, 0.5)  # デフォルト値0.5
    
    def calculate_flow(self, rainfall_data: Dict[float, float], dtq: float) -> Dict[float, float]:
        """
        合成合理式を使用して流量を計算
        Q = 1/3.6 * f * r * A
        
        Parameters:
        -----------
        rainfall_data : Dict[float, float]
            時刻と雨量のディクショナリ {時刻(s): 雨量(mm/h)}
        dtq : float
            出力する時間間隔(s)
            
        Returns:
        --------
        Dict[float, float]
            時刻と流量のディクショナリ {時刻(s): 流量(m3/s)}
        """
        if self.arrival_time is None or self.landuse is None:
            raise ValueError("Data must be loaded first")
        
        nodata = self.gis_reader.metadata.nodata
        
        # 計算時間の設定
        times = np.array(sorted(rainfall_data.keys()))
        max_time = max(times)
        max_arrival_time = np.max(self.arrival_time[self.arrival_time != nodata])
        total_time = max_time + max_arrival_time
        
        # 出力時刻の設定
        output_times = np.arange(0, total_time + dtq, dtq)
        flow_results = {t: 0.0 for t in output_times}
        
        # 有効なセルのマスク
        valid_mask = (self.arrival_time != nodata) & (self.landuse != nodata)
        
        # 各セルの寄与を計算
        for i in range(self.arrival_time.shape[0]):
            for j in range(self.arrival_time.shape[1]):
                if valid_mask[i, j]:
                    # セルの特性を取得
                    arrival_t = self.arrival_time[i, j]
                    f = self.get_runoff_coefficient(int(self.landuse[i, j]))
                    
                    # 各時刻での流量を計算
                    for t, r in rainfall_data.items():
                        # 到達時刻を計算
                        reach_time = t + arrival_t
                        
                        # 対応する出力時刻を見つける
                        output_t = dtq * np.floor(reach_time / dtq)
                        if output_t in flow_results:
                            # 合成合理式による流量計算
                            # Q = 1/3.6 * f * r * A
                            dq = (1/3.6) * f * r * (self.cell_area / 1000000)  # m²からkm²に変換
                            flow_results[output_t] += dq
        
        return flow_results

    def export_results(self, flow_results: Dict[float, float], output_file: str):
        """
        計算結果をCSVファイルとして出力
        
        Parameters:
        -----------
        flow_results : Dict[float, float]
            時刻と流量のディクショナリ
        output_file : str
            出力ファイルパス
        """
        with open(output_file, 'w') as f:
            f.write('Time(s),Flow(m3/s)\n')
            for t in sorted(flow_results.keys()):
                f.write(f'{t:.1f},{flow_results[t]:.6f}\n')

    def get_total_area(self) -> float:
        """
        有効なセルの総面積を計算
        
        Returns:
        --------
        float
            総面積(m2)
        """
        if self.landuse is None:
            raise ValueError("Data must be loaded first")
            
        valid_cells = np.sum(self.landuse != self.gis_reader.metadata.nodata)
        return valid_cells * self.cell_area
