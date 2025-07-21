"""
スプレッドシート関連の定数定義

Google Sheetsで使用するシート名、列名、その他の定数をEnumクラスで定義します。
"""

from enum import Enum
from pathlib import Path

import yaml


class CleaningRecordsSheet(str, Enum):
    """掃除記録シートの定数"""

    SHEET_NAME = "掃除記録"
    DATETIME = "日時"
    TYPE = "掃除種別"
    RECORDER = "記録者"
    NOTE = "備考"


class CleaningSettingsSheet(str, Enum):
    """掃除種別設定シートの定数"""

    SHEET_NAME = "掃除種別設定"
    TYPE = "掃除種別"
    FREQUENCY = "推奨頻度（日）"
    LAST_DATE = "最終実施日"
    NEXT_DATE = "次回予定日"
    PRIORITY = "優先度"


class ColumnLetter(str, Enum):
    """スプレッドシートの列文字（A, B, C...）"""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"  # noqa: E741
    J = "J"


class Priority(str, Enum):
    """掃除の優先度"""

    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class DefaultValue(Enum):
    """デフォルト値"""

    RECORDER = "Alexa音声入力"
    FREQUENCY = 7


def _load_default_cleaning_settings():
    """YAMLファイルからデフォルト掃除種別設定を読み込む"""
    try:
        # Lambda環境とローカル環境の両方に対応したパス解決
        current_dir = Path(__file__).parent

        # 複数のパスを試行（Lambda環境とローカル環境の違いに対応）
        possible_paths = [
            current_dir.parent / "config" / "default_cleaning_settings.yaml",  # ローカル環境
            current_dir / "config" / "default_cleaning_settings.yaml",  # Lambda環境（srcと同じレベル）
            Path("config") / "default_cleaning_settings.yaml",  # Lambda環境（ルートレベル）
            Path("default_cleaning_settings.yaml"),  # Lambda環境（直接ルート）
        ]

        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break

        if config_path is None:
            raise FileNotFoundError(f"YAMLファイルが見つかりません。試行したパス: {possible_paths}")

        print(f"YAMLファイルを読み込み中: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # ヘッダー行を作成
        settings = [
            [
                CleaningSettingsSheet.TYPE,
                CleaningSettingsSheet.FREQUENCY,
                CleaningSettingsSheet.LAST_DATE,
                CleaningSettingsSheet.NEXT_DATE,
                CleaningSettingsSheet.PRIORITY,
            ]
        ]

        # 各掃除種別の設定を追加
        for cleaning_type in config["cleaning_types"]:
            settings.append(
                [
                    cleaning_type["name"],
                    str(cleaning_type["frequency"]),
                    "",  # 最終実施日は空
                    "",  # 次回予定日は空
                    cleaning_type["priority"],
                ]
            )

        return settings

    except Exception as e:
        # YAMLファイルの読み込みに失敗した場合のフォールバック
        print(f"警告: デフォルト設定YAMLファイルの読み込みに失敗しました: {e}")
        print(f"現在の作業ディレクトリ: {Path.cwd()}")
        print(f"__file__の場所: {Path(__file__).parent}")

        # ディレクトリ構造をデバッグ出力
        try:
            current_dir = Path(__file__).parent
            print(f"現在のディレクトリ内容: {list(current_dir.iterdir())}")
            if current_dir.parent.exists():
                print(f"親ディレクトリの内容: {list(current_dir.parent.iterdir())}")
            if Path.cwd() != current_dir:
                print(f"作業ディレクトリの内容: {list(Path.cwd().iterdir())}")
        except Exception as debug_e:
            print(f"ディレクトリ構造のデバッグ中にエラー: {debug_e}")

        print("フォールバック設定を使用します")

        return [
            [
                CleaningSettingsSheet.TYPE,
                CleaningSettingsSheet.FREQUENCY,
                CleaningSettingsSheet.LAST_DATE,
                CleaningSettingsSheet.NEXT_DATE,
                CleaningSettingsSheet.PRIORITY,
            ],
            ["トイレ掃除", "3", "", "", Priority.HIGH],
            ["風呂掃除", "7", "", "", Priority.HIGH],
            ["キッチン掃除", "3", "", "", Priority.HIGH],
            ["床掃除", "7", "", "", Priority.MEDIUM],
            ["窓掃除", "14", "", "", Priority.LOW],
            ["掃除機かけ", "3", "", "", Priority.MEDIUM],
        ]


class SheetConstants:
    """スプレッドシート関連の定数を提供するクラス"""

    # ヘッダー行の定義
    CLEANING_RECORDS_HEADERS = [
        CleaningRecordsSheet.DATETIME,
        CleaningRecordsSheet.TYPE,
        CleaningRecordsSheet.RECORDER,
        CleaningRecordsSheet.NOTE,
    ]

    CLEANING_SETTINGS_HEADERS = [
        CleaningSettingsSheet.TYPE,
        CleaningSettingsSheet.FREQUENCY,
        CleaningSettingsSheet.LAST_DATE,
        CleaningSettingsSheet.NEXT_DATE,
        CleaningSettingsSheet.PRIORITY,
    ]

    # 掃除種別設定シートの列とスプレッドシート列文字のマッピング
    SETTINGS_COLUMN_MAPPING = {
        CleaningSettingsSheet.TYPE: ColumnLetter.A,
        CleaningSettingsSheet.FREQUENCY: ColumnLetter.B,
        CleaningSettingsSheet.LAST_DATE: ColumnLetter.C,
        CleaningSettingsSheet.NEXT_DATE: ColumnLetter.D,
        CleaningSettingsSheet.PRIORITY: ColumnLetter.E,
    }

    # 優先度の順序
    PRIORITY_ORDER = {
        Priority.HIGH: 0,
        Priority.MEDIUM: 1,
        Priority.LOW: 2,
    }

    # デフォルトの掃除種別設定（YAMLから動的に読み込み）
    DEFAULT_CLEANING_SETTINGS = _load_default_cleaning_settings()
