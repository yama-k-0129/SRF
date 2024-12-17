# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

import numpy as np
from ..models.metadata import GISMetadata

class CellSizeCalculator:
    """緯度経度からメートル単位のセルサイズを計算するクラス"""
    
    def __init__(self):
        # 定数の設定
        self.SEMI_MAJOR_AXIS = 6378137.000  # 地球の長半径 (a)
        self.SEMI_MINOR_AXIS = 6356752.314  # 地球の短半径 (b)
        self.PI = np.pi
        
    def hubeny_distance(self, x1_deg: float, y1_deg: float, x2_deg: float, y2_deg: float) -> float:
        """
        2点間の距離をHubenyの式で計算
        
        Parameters:
        -----------
        x1_deg, y1_deg : float
            始点の経度、緯度（度）
        x2_deg, y2_deg : float
            終点の経度、緯度（度）
            
        Returns:
        --------
        float
            2点間の距離（メートル）
        """
        # 度からラジアンに変換
        x1 = x1_deg * self.PI / 180.0
        y1 = y1_deg * self.PI / 180.0
        x2 = x2_deg * self.PI / 180.0
        y2 = y2_deg * self.PI / 180.0
        
        # 緯度差、経度差、平均緯度
        dy = y1 - y2
        dx = x1 - x2
        mu = (y1 + y2) / 2.0
        
        # 扁平率に関する計算
        e2 = (self.SEMI_MAJOR_AXIS**2 - self.SEMI_MINOR_AXIS**2) / self.SEMI_MAJOR_AXIS**2
        w = np.sqrt(1 - e2 * (np.sin(mu))**2)
        
        # 子午線曲率半径と卯酉線曲率半径
        n = self.SEMI_MAJOR_AXIS / w
        m = self.SEMI_MAJOR_AXIS * (1 - e2) / w**3
        
        # 距離の計算
        d = np.sqrt((dy * m)**2 + (dx * n * np.cos(mu))**2)
        
        return d
    
    def calculate_cell_size(self, metadata: GISMetadata) -> tuple:
        """
        セルサイズを計算
        
        Parameters:
        -----------
        metadata : GISMetadata
            GISファイルのメタデータ
            
        Returns:
        --------
        tuple
            (dx, dy, length, area) : セルの東西・南北サイズ(m)、代表長さ(m)、面積(m2)
        """
        nx = metadata.nx
        ny = metadata.ny
        xll = metadata.xllcorner
        yll = metadata.yllcorner
        cellsize = metadata.cellsize
        
        # 南側の長さ (d1)
        d1 = self.hubeny_distance(
            xll, yll,
            xll + nx * cellsize, yll
        )
        
        # 北側の長さ (d2)
        d2 = self.hubeny_distance(
            xll, yll + ny * cellsize,
            xll + nx * cellsize, yll + ny * cellsize
        )
        
        # 西側の長さ (d3)
        d3 = self.hubeny_distance(
            xll, yll,
            xll, yll + ny * cellsize
        )
        
        # 東側の長さ (d4)
        d4 = self.hubeny_distance(
            xll + nx * cellsize, yll,
            xll + nx * cellsize, yll + ny * cellsize
        )
        
        # 平均セルサイズの計算
        dx = (d1 + d2) / (2.0 * nx)
        dy = (d3 + d4) / (2.0 * ny)
        
        # セルの代表長さと面積
        length = np.sqrt(dx * dy)
        area = dx * dy
        
        return dx, dy, length, area