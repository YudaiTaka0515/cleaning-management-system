"""
Google Sheets管理モジュール

Googleスプレッドシートとの連携を管理するクラスを提供します。
掃除記録の保存、掃除種別設定の管理、期限切れ掃除の検出などを行います。
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict

from .sheet_constants import (
    CleaningRecordsSheet,
    CleaningSettingsSheet,
    Priority,
    DefaultValue,
    SheetConstants,
)

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Google Sheetsの操作を管理するクラス"""

    def __init__(self):
        """Google Sheetsマネージャーを初期化"""
        self.gc = None
        self.spreadsheet = None
        self._initialize()

    def _initialize(self):
        """Google Sheetsクライアントを初期化"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            service_account_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
            if not service_account_key:
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY環境変数が設定されていません")

            service_account_info = json.loads(service_account_key)
            credentials = Credentials.from_service_account_info(
                service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            self.gc = gspread.authorize(credentials)

            spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("GOOGLE_SPREADSHEET_ID環境変数が設定されていません")

            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            logger.info(f"✅ Google Sheets初期化成功: {self.spreadsheet.title}")

        except Exception as e:
            logger.error(f"❌ Google Sheets初期化エラー: {e}")
            raise

    def get_or_create_cleaning_sheet(self):
        """掃除記録シートを取得または作成"""
        try:
            return self.spreadsheet.worksheet(CleaningRecordsSheet.SHEET_NAME)
        except Exception:  # gspread.WorksheetNotFoundを含む全ての例外をキャッチ
            logger.info("掃除記録シートを新規作成中...")
            sheet = self.spreadsheet.add_worksheet(title=CleaningRecordsSheet.SHEET_NAME, rows=1000, cols=10)
            sheet.update("A1:D1", [SheetConstants.CLEANING_RECORDS_HEADERS])
            logger.info("✅ 掃除記録シート作成完了")
            return sheet

    def get_or_create_settings_sheet(self):
        """掃除種別設定シートを取得または作成"""
        try:
            return self.spreadsheet.worksheet(CleaningSettingsSheet.SHEET_NAME)
        except Exception:  # gspread.WorksheetNotFoundを含む全ての例外をキャッチ
            logger.info("掃除種別設定シートを新規作成中...")
            sheet = self.spreadsheet.add_worksheet(title=CleaningSettingsSheet.SHEET_NAME, rows=100, cols=10)

            # デフォルト設定を追加（より安全な書き込み方法）
            default_settings = SheetConstants.DEFAULT_CLEANING_SETTINGS
            num_rows = len(default_settings)
            logger.info(f"📊 デフォルト設定を書き込み中: {num_rows}行のデータ")

            # 行ごとに書き込み（より確実）
            for i, row_data in enumerate(default_settings, 1):
                try:
                    range_spec = f"A{i}:E{i}"
                    sheet.update(range_spec, [row_data])
                    logger.debug(f"✅ 行{i}書き込み完了: {row_data[0]}")
                except Exception as row_error:
                    logger.error(f"❌ 行{i}書き込みエラー: {row_error}")
                    # 個別の行エラーは継続
                    continue
            logger.info("✅ 掃除種別設定シート作成完了")
            return sheet

    def add_cleaning_record(self, cleaning_type: str, note: str = "") -> bool:
        """
        掃除記録を追加

        Args:
            cleaning_type: 掃除の種類
            note: 備考（オプション）

        Returns:
            bool: 成功した場合True
        """
        try:
            sheet = self.get_or_create_cleaning_sheet()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record_data = [timestamp, cleaning_type, DefaultValue.RECORDER.value, note]

            # より安全な書き込み方法：append_rowを使用
            try:
                sheet.append_row(record_data)
                logger.info(f"✅ 掃除記録追加成功（append_row使用）: {cleaning_type}")
            except Exception as append_error:
                logger.warning(f"⚠️ append_row失敗、手動で行を検索: {append_error}")
                # フォールバック：手動で次の行を見つけて追加
                all_values = sheet.get_all_values()
                next_row = len(all_values) + 1
                range_spec = f"A{next_row}:D{next_row}"
                sheet.update(range_spec, [record_data])
                logger.info(f"✅ 掃除記録追加成功（手動範囲指定）: {cleaning_type} at row {next_row}")

            # 掃除種別設定の最終実施日を更新
            self._update_last_cleaning_date(cleaning_type, timestamp)

            return True

        except Exception as e:
            logger.error(f"❌ 掃除記録追加エラー: {e}")
            return False

    def _update_last_cleaning_date(self, cleaning_type: str, timestamp: str):
        """
        掃除種別設定の最終実施日を更新

        Args:
            cleaning_type: 掃除の種類
            timestamp: 実施日時
        """
        try:
            settings_sheet = self.get_or_create_settings_sheet()
            records = settings_sheet.get_all_records()

            for i, record in enumerate(records):
                if record.get(CleaningSettingsSheet.TYPE) == cleaning_type:
                    row_num = i + 2  # ヘッダー行を考慮
                    logger.info(f"📍 {cleaning_type}の設定を行{row_num}で更新中")

                    try:
                        # 最終実施日を更新
                        last_date_col = SheetConstants.SETTINGS_COLUMN_MAPPING[CleaningSettingsSheet.LAST_DATE]
                        last_date_range = f"{last_date_col}{row_num}"
                        settings_sheet.update(last_date_range, [[timestamp]])
                        logger.debug(f"✅ 最終実施日更新: {last_date_range} = {timestamp}")

                        # 次回予定日を計算
                        frequency = int(record.get(CleaningSettingsSheet.FREQUENCY, DefaultValue.FREQUENCY.value))
                        next_date = (
                            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=frequency)
                        ).strftime("%Y-%m-%d")
                        next_date_col = SheetConstants.SETTINGS_COLUMN_MAPPING[CleaningSettingsSheet.NEXT_DATE]
                        next_date_range = f"{next_date_col}{row_num}"
                        settings_sheet.update(next_date_range, [[next_date]])
                        logger.debug(f"✅ 次回予定日更新: {next_date_range} = {next_date}")

                        logger.info(f"✅ 最終実施日更新完了: {cleaning_type} -> {timestamp} (次回: {next_date})")
                        break

                    except Exception as update_error:
                        logger.error(f"❌ 行{row_num}の更新エラー: {update_error}")
                        continue

            else:
                logger.warning(f"⚠️ 掃除種別'{cleaning_type}'が設定シートに見つかりません")

        except Exception as e:
            logger.error(f"❌ 最終実施日更新エラー: {e}")
            import traceback

            logger.error(f"❌ 詳細エラー: {traceback.format_exc()}")

    def get_cleaning_records(self) -> List[Dict]:
        """
        掃除記録を取得

        Returns:
            List[Dict]: 掃除記録のリスト
        """
        try:
            sheet = self.get_or_create_cleaning_sheet()
            records = sheet.get_all_records()
            logger.info(f"✅ 掃除記録取得成功: {len(records)}件")
            return records
        except Exception as e:
            logger.error(f"❌ 掃除記録取得エラー: {e}")
            return []

    def get_overdue_cleanings(self) -> List[Dict]:
        """
        期限切れの掃除種別を取得

        Returns:
            List[Dict]: 期限切れの掃除リスト（優先度順）
        """
        try:
            settings_sheet = self.get_or_create_settings_sheet()
            records = settings_sheet.get_all_records()
            overdue_list = []
            today = datetime.now().date()

            for record in records:
                next_date_str = record.get(CleaningSettingsSheet.NEXT_DATE, "")
                if next_date_str:
                    try:
                        next_date = datetime.strptime(next_date_str, "%Y-%m-%d").date()
                        if next_date <= today:
                            overdue_list.append(
                                {
                                    "type": record.get(CleaningSettingsSheet.TYPE),
                                    "priority": record.get(CleaningSettingsSheet.PRIORITY, Priority.MEDIUM),
                                    "days_overdue": (today - next_date).days,
                                    "frequency": record.get(
                                        CleaningSettingsSheet.FREQUENCY, DefaultValue.FREQUENCY.value
                                    ),
                                }
                            )
                    except ValueError:
                        # 日付フォーマットが不正な場合はスキップ
                        continue

            # 優先度と遅延日数でソート
            overdue_list.sort(key=lambda x: (SheetConstants.PRIORITY_ORDER.get(x["priority"], 1), -x["days_overdue"]))

            logger.info(f"✅ 期限切れ掃除取得成功: {len(overdue_list)}件")
            return overdue_list

        except Exception as e:
            logger.error(f"❌ 期限切れ掃除取得エラー: {e}")
            return []

    def get_cleaning_settings(self) -> List[Dict]:
        """
        掃除種別設定を取得

        Returns:
            List[Dict]: 掃除種別設定のリスト
        """
        try:
            settings_sheet = self.get_or_create_settings_sheet()
            records = settings_sheet.get_all_records()
            logger.info(f"✅ 掃除種別設定取得成功: {len(records)}件")
            return records
        except Exception as e:
            logger.error(f"❌ 掃除種別設定取得エラー: {e}")
            return []
