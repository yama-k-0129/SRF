# Copyright (c) 2024 yama-k-0129
# 
# This software is released under the MIT License.
# see https://opensource.org/licenses/MIT

import yaml
from typing import Dict, Any, Optional

class ConfigManager:
    """設定ファイルを管理するクラス"""
    
    # 必須のセクションリスト
    REQUIRED_SECTIONS = ['file_paths', 'parameters', 'analysis_points']
    
    def __init__(self, config_path: str):
        """
        Parameters:
        -----------
        config_path : str
            設定ファイルのパス
        
        Raises:
        -------
        ValueError
            必須のセクションが設定ファイルに存在しない場合
        RuntimeError
            設定ファイルの読み込みに失敗した場合
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
        
    def _load_config(self) -> dict:
        """
        YAMLファイルから設定を読み込む
        
        Returns:
        --------
        dict
            設定データ
        
        Raises:
        -------
        RuntimeError
            ファイルの読み込みに失敗した場合
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading config file: {str(e)}")
    
    def _validate_config(self) -> None:
        """
        設定ファイルの構造を検証する
        
        Raises:
        -------
        ValueError
            必須のセクションが存在しない場合
        """
        missing_sections = [
            section for section in self.REQUIRED_SECTIONS
            if section not in self.config
        ]
        if missing_sections:
            raise ValueError(
                f"Required sections missing in config file: {', '.join(missing_sections)}"
            )
    
    @property
    def file_paths(self) -> dict:
        """
        ファイルパスの設定を取得
        
        Returns:
        --------
        dict
            ファイルパスの設定
        """
        return self.config.get('file_paths', {})
    
    @property
    def parameters(self) -> dict:
        """
        計算パラメータの設定を取得
        
        Returns:
        --------
        dict
            計算パラメータの設定
        """
        return self.config.get('parameters', {})
    
    @property
    def analysis_points(self) -> dict:
        """
        解析地点の設定を取得
        
        Returns:
        --------
        dict
            解析地点の設定
        """
        return self.config.get('analysis_points', {})
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """
        指定されたセクションとキーの値を取得する
        
        Parameters:
        -----------
        section : str
            セクション名
        key : str
            キー名
        default : Any, optional
            デフォルト値（デフォルト: None）
        
        Returns:
        --------
        Any
            設定値。セクションまたはキーが存在しない場合はデフォルト値
        """
        return self.config.get(section, {}).get(key, default)
    
    def validate_required_keys(self, section: str, required_keys: list) -> None:
        """
        指定されたセクション内の必須キーの存在を検証する
        
        Parameters:
        -----------
        section : str
            検証するセクション名
        required_keys : list
            必須キーのリスト
        
        Raises:
        -------
        ValueError
            必須キーが存在しない場合
        """
        if section not in self.config:
            raise ValueError(f"Section '{section}' not found in config file")
            
        section_data = self.config[section]
        missing_keys = [
            key for key in required_keys
            if key not in section_data
        ]
        
        if missing_keys:
            raise ValueError(
                f"Required keys missing in section '{section}': {', '.join(missing_keys)}"
            )