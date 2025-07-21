"""
アプリケーション設定モジュール

環境変数やアプリケーションの設定を管理します。
"""

import os
from enum import Enum

try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


class Priority(str, Enum):
    """掃除の優先度"""

    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class CleaningType(str, Enum):
    """掃除種別"""

    TOILET = "トイレ掃除"
    BATHROOM = "風呂掃除"
    KITCHEN = "キッチン掃除"
    FLOOR = "床掃除"
    WINDOW = "窓掃除"
    VACUUM = "掃除機かけ"


class AppConfig:
    """アプリケーション設定クラス"""

    # Google Sheets設定（環境変数またはStreamlit Secrets）
    @staticmethod
    def get_google_service_account_key():
        if HAS_STREAMLIT and hasattr(st, "secrets"):
            try:
                return st.secrets["google"]["service_account_key"]
            except (KeyError, AttributeError):
                pass
        return os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")

    @staticmethod
    def get_google_spreadsheet_id():
        if HAS_STREAMLIT and hasattr(st, "secrets"):
            try:
                return st.secrets["google"]["spreadsheet_id"]
            except (KeyError, AttributeError):
                pass
        return os.environ.get("GOOGLE_SPREADSHEET_ID")

    # 後方互換性のためのプロパティ
    @property
    def GOOGLE_SERVICE_ACCOUNT_KEY(self):
        return self.get_google_service_account_key()

    @property
    def GOOGLE_SPREADSHEET_ID(self):
        return self.get_google_spreadsheet_id()

    # シート名
    CLEANING_RECORDS_SHEET = "掃除記録"
    CLEANING_SETTINGS_SHEET = "掃除種別設定"

    # 自動更新間隔（秒）
    AUTO_REFRESH_INTERVAL = 300  # 5分

    # 掃除種別の設定
    CLEANING_TYPES_CONFIG = {
        CleaningType.TOILET: {"frequency": 3, "priority": Priority.HIGH, "color": "#FF6B6B"},
        CleaningType.BATHROOM: {"frequency": 7, "priority": Priority.HIGH, "color": "#4ECDC4"},
        CleaningType.KITCHEN: {"frequency": 3, "priority": Priority.HIGH, "color": "#45B7D1"},
        CleaningType.FLOOR: {"frequency": 7, "priority": Priority.MEDIUM, "color": "#96CEB4"},
        CleaningType.WINDOW: {"frequency": 14, "priority": Priority.LOW, "color": "#FFEAA7"},
        CleaningType.VACUUM: {"frequency": 3, "priority": Priority.MEDIUM, "color": "#DDA0DD"},
    }

    # 優先度の色設定
    PRIORITY_COLORS = {Priority.HIGH: "#FF4444", Priority.MEDIUM: "#FFA500", Priority.LOW: "#90EE90"}


class ValidationError(Exception):
    """設定値の検証エラー"""

    pass


def validate_config() -> None:
    """設定値の検証"""
    config = AppConfig()

    if not config.GOOGLE_SERVICE_ACCOUNT_KEY:
        raise ValidationError("GOOGLE_SERVICE_ACCOUNT_KEY環境変数またはStreamlit Secretsが設定されていません")

    if not config.GOOGLE_SPREADSHEET_ID:
        raise ValidationError("GOOGLE_SPREADSHEET_ID環境変数またはStreamlit Secretsが設定されていません")


def get_cleaning_type_color(cleaning_type: str) -> str:
    """掃除種別の色を取得"""
    for ct in CleaningType:
        if ct.value == cleaning_type:
            return AppConfig.CLEANING_TYPES_CONFIG[ct]["color"]
    return "#808080"  # デフォルト色


def get_priority_color(priority: str) -> str:
    """優先度の色を取得"""
    for p in Priority:
        if p.value == priority:
            return AppConfig.PRIORITY_COLORS[p]
    return "#808080"  # デフォルト色
