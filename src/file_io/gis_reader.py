# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

import numpy as np
from typing import Tuple, Optional
from ..models.metadata import GISMetadata

class GISDataReader:
    def __init__(self):
        self.metadata: Optional[GISMetadata] = None
        
    def read_gis_file(self, filepath: str, expected_metadata: Optional[GISMetadata] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        ASC形式のGISファイルを高速に読み込む
        ASCファイルは南西端が原点で、北に向かってy方向、東に向かってx方向に展開
        """
        try:
            # メタデータ行を読み込む
            with open(filepath, 'r') as f:
                metadata = {}
                for _ in range(6):
                    key, value = f.readline().strip().split()
                    metadata[key.lower()] = float(value)

            # メタデータを設定
            self.metadata = GISMetadata(
                nx=int(metadata['ncols']),
                ny=int(metadata['nrows']),
                xllcorner=metadata['xllcorner'],
                yllcorner=metadata['yllcorner'],
                cellsize=metadata['cellsize'],
                nodata=metadata['nodata_value']
            )

            # 検証が必要な場合のみ実行
            if expected_metadata:
                self._validate_metadata(expected_metadata)

            # データを読み込み（上から下の順）
            data = np.loadtxt(filepath, skiprows=6)
            
            # y座標は下から上に向かって増加するため、データを上下反転
            data = np.flipud(data)

            # x座標配列（西から東へ）
            x = np.linspace(
                self.metadata.xllcorner,
                self.metadata.xllcorner + self.metadata.cellsize * (self.metadata.nx - 1),
                self.metadata.nx
            )
            
            # y座標配列（南から北へ）
            y = np.linspace(
                self.metadata.yllcorner,
                self.metadata.yllcorner + self.metadata.cellsize * (self.metadata.ny - 1),
                self.metadata.ny
            )
            
            # メッシュグリッドの生成（indexing='ij'を使用して正しい順序を保証）
            x_coords, y_coords = np.meshgrid(x, y, indexing='ij')
            
            # データと座標の形状を合わせるためにデータを転置
            data = data.T
            
            return data, x_coords, y_coords

        except Exception as e:
            raise RuntimeError(f"Error reading GIS file: {str(e)}")

    def _validate_metadata(self, expected: GISMetadata):
        """必要最小限のメタデータ検証"""
        if self.metadata.nx != expected.nx or self.metadata.ny != expected.ny:
            raise ValueError(f"Invalid dimensions: expected {expected.nx}x{expected.ny}, got {self.metadata.nx}x{self.metadata.ny}")
        if abs(self.metadata.cellsize - expected.cellsize) > 0.01:
            raise ValueError(f"Invalid cellsize: expected {expected.cellsize}, got {self.metadata.cellsize}")
    
    def export_to_asc(self, data: np.ndarray, output_filepath: str):
        """
        データをASC形式で出力する
        
        Parameters:
        -----------
        data: np.ndarray
            出力するデータ配列
        output_filepath: str
            出力ファイルパス
        """
        if self.metadata is None:
            raise ValueError("Metadata is not set. Please read a GIS file first.")
            
        # データを元の向きに戻す
        output_data = data.T
        output_data = np.flipud(output_data)
        
        # ASCファイルとして出力
        with open(output_filepath, 'w') as f:
            # メタデータの書き込み
            f.write(f"NCOLS {self.metadata.nx}\n")
            f.write(f"NROWS {self.metadata.ny}\n")
            f.write(f"XLLCORNER {self.metadata.xllcorner}\n")
            f.write(f"YLLCORNER {self.metadata.yllcorner}\n")
            f.write(f"CELLSIZE {self.metadata.cellsize}\n")
            f.write(f"NODATA_VALUE {self.metadata.nodata}\n")
            
            # データの書き込み
            np.savetxt(f, output_data, fmt='%.1f')