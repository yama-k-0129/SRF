# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

import numpy as np
from ..file_io.gis_reader import GISDataReader

class FloodArrivalCalculator:
    """洪水到達時間を計算するクラス"""
    
    def __init__(self, gis_reader: GISDataReader):
        """
        Parameters:
        -----------
        gis_reader : GISDataReader
            GISデータを読み込むためのリーダークラスのインスタンス
        """
        self.gis_reader = gis_reader
        self.distance_data = None
        self.elevation_data = None
        
    def load_data(self, distance_file: str, elevation_file: str):
        """
        距離データと標高データを読み込む
        
        Parameters:
        -----------
        distance_file : str
            距離データのファイルパス
        elevation_file : str
            標高データのファイルパス
        """
        # 距離データの読み込み
        self.distance_data, _, _ = self.gis_reader.read_gis_file(distance_file)
        
        # 標高データの読み込み（距離データのメタデータを使用して検証）
        self.elevation_data, _, _ = self.gis_reader.read_gis_file(
            elevation_file, 
            expected_metadata=self.gis_reader.metadata
        )
    
    @staticmethod
    def calculate_velocity(slope: float) -> float:
        """
        勾配から流速を計算
        
        Parameters:
        -----------
        slope : float
            勾配
            
        Returns:
        --------
        float
            流速 (m/s)
        """
        if slope >= 0.01:  # 1/100以上
            return 3.5
        elif slope >= 0.005:  # 1/200以上1/100未満
            return 3.0
        else:  # 1/200未満
            return 2.1
    
    def calculate_arrival_time(self) -> np.ndarray:
        """
        洪水到達時間を計算
        
        Returns:
        --------
        np.ndarray
            洪水到達時間の配列
        """
        if self.distance_data is None or self.elevation_data is None:
            raise ValueError("Distance and elevation data must be loaded first")
        
        nodata = self.gis_reader.metadata.nodata
        arrival_time = np.full_like(self.distance_data, nodata)
        
        # データが存在する部分のみ計算
        valid_mask = (self.distance_data != nodata) & (self.elevation_data != nodata)
        
        # 勾配の計算
        valid_distances = self.distance_data > 0
        slopes = np.zeros_like(self.distance_data)
        slopes[valid_distances] = np.abs(
            self.elevation_data[valid_distances] / self.distance_data[valid_distances]
        )
        
        # 速度の計算（配列演算を使用）
        velocities = np.where(slopes >= 0.01, 3.5,
                    np.where(slopes >= 0.005, 3.0, 2.1))
        
        # 到達時間の計算
        arrival_time[valid_mask] = self.distance_data[valid_mask] / velocities[valid_mask]
        
        return arrival_time
    
    def process_and_save(self, distance_file: str, elevation_file: str, output_file: str):
        """
        データの読み込みから計算、保存までの一連の処理を実行
        
        Parameters:
        -----------
        distance_file : str
            距離データのファイルパス
        elevation_file : str
            標高データのファイルパス
        output_file : str
            出力ファイルパス
        """
        # データの読み込み
        self.load_data(distance_file, elevation_file)
        
        # 到達時間の計算
        arrival_time = self.calculate_arrival_time()
        
        # 結果の保存
        self.gis_reader.export_to_asc(arrival_time, output_file)