# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

import yaml
from typing import Dict

class ConfigManager:
    """設定ファイルを管理するクラス"""
    
    def __init__(self, config_path: str):
        """
        Parameters:
        -----------
        config_path : str
            設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """
        YAMLファイルから設定を読み込む
        
        Returns:
        --------
        dict
            設定データ
        """
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading config file: {str(e)}")
    
    @property
    def file_paths(self) -> dict:
        """ファイルパスの設定を取得"""
        return self.config.get('file_paths', {})
    
    @property
    def parameters(self) -> dict:
        """計算パラメータの設定を取得"""
        return self.config.get('parameters', {})
