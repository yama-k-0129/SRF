# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

from typing import Dict

def read_rainfall_data(rainfall_file: str) -> Dict[float, float]:
    """
    CSVファイルから雨量データを読み込む
    
    Parameters:
    -----------
    rainfall_file : str
        雨量データのCSVファイルパス
        
    Returns:
    --------
    Dict[float, float]
        時刻と雨量のディクショナリ {時刻(s): 雨量(mm/h)}
    """
    rainfall_data = {}
    
    try:
        with open(rainfall_file, 'r') as f:
            # ヘッダー行をスキップ
            header = f.readline().strip()
            
            # 各行を読み込み
            for line in f:
                # カンマで分割してデータを取得
                time_str, rainfall_str = line.strip().split(',')
                
                # 時刻を秒単位に変換（時刻が時:分:秒形式の場合）
                try:
                    h, m, s = map(float, time_str.split(':'))
                    time_seconds = h * 3600 + m * 60 + s
                except ValueError:
                    # 時刻が秒単位で記録されている場合
                    time_seconds = float(time_str)
                
                # 雨量を float に変換
                rainfall = float(rainfall_str)
                
                # データを辞書に追加
                rainfall_data[time_seconds] = rainfall
                
        return rainfall_data
    
    except Exception as e:
        raise RuntimeError(f"Error reading rainfall data: {str(e)}")