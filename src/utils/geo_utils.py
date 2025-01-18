# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

from typing import Tuple
import math
import numpy as np
from ..models.metadata import GISMetadata

def find_nearest_point_data(
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    data: np.ndarray,
    target_lon: float,
    target_lat: float,
    xllcorner: float,
    yllcorner: float,
    cellsize: float,
    threshold: float,
    metadata: GISMetadata  # 追加
) -> Tuple[float, float, float, bool, int, int]:
    """
    指定された緯度・経度に最も近い格子点のデータを検索し、閾値判定を行う
    格子のインデックスを使用して検索を行う
    """
    # 目標地点と南西端との差分を計算
    dx = target_lon - xllcorner
    dy = target_lat - yllcorner
    
    # セルサイズで割って、インデックスを計算(1スタートpython用)
    x_index1 = math.ceil(dx / cellsize)
    y_index1 = math.ceil(dy / cellsize)
    
    # セルサイズで割って、インデックスを計算(0スタートpython用)
    x_index0 = x_index1 - 1
    y_index0 = y_index1 - 1
    
    # 該当するグリッドポイントの座標とデータを取得
    nearest_x = x_coords[x_index0, y_index0]
    nearest_y = y_coords[x_index0, y_index0]
    value = data[x_index0, y_index0]
    
    # 閾値判定
    is_above_threshold = value > threshold
    
    # メッシュ番号変換
    i0 = metadata.ny - y_index1 + 1  # readerの参照を削除
    j0 = x_index1
    
    return nearest_x, nearest_y, value, is_above_threshold, i0, j0