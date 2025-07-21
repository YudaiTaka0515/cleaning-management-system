"""
データ管理モジュール

Google Sheetsからデータを取得し、アプリケーションで使用可能な形式に変換します。
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

from .config import AppConfig


logger = logging.getLogger(__name__)


class DataManager:
    """データ管理クラス"""

    def __init__(self):
        """データマネージャーを初期化"""
        self.gc = None
        self.spreadsheet = None
        self._initialize_google_sheets()

    def _initialize_google_sheets(self) -> None:
        """Google Sheetsクライアントを初期化"""
        try:
            config = AppConfig()
            service_account_key = config.GOOGLE_SERVICE_ACCOUNT_KEY
            spreadsheet_id = config.GOOGLE_SPREADSHEET_ID

            if not service_account_key:
                st.error("GOOGLE_SERVICE_ACCOUNT_KEY環境変数またはStreamlit Secretsが設定されていません")
                st.stop()

            if not spreadsheet_id:
                st.error("GOOGLE_SPREADSHEET_ID環境変数またはStreamlit Secretsが設定されていません")
                st.stop()

            service_account_info = json.loads(service_account_key)
            credentials = Credentials.from_service_account_info(
                service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )

            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)

            logger.info("Google Sheets初期化完了")

        except Exception as e:
            logger.error(f"Google Sheets初期化エラー: {e}")
            st.error(f"Google Sheets初期化エラー: {e}")
            st.stop()

    @st.cache_data(ttl=AppConfig.AUTO_REFRESH_INTERVAL)
    def get_cleaning_records(_self) -> pd.DataFrame:
        """掃除記録データを取得"""
        try:
            sheet = _self.spreadsheet.worksheet(AppConfig.CLEANING_RECORDS_SHEET)
            records = sheet.get_all_records()

            if not records:
                return pd.DataFrame(columns=["日時", "掃除種別", "記録者", "備考"])

            df = pd.DataFrame(records)

            # 日時列を datetime型に変換
            if "日時" in df.columns:
                df["日時"] = pd.to_datetime(df["日時"], errors="coerce")

            # 最新の記録を先頭に
            df = df.sort_values("日時", ascending=False)

            logger.info(f"掃除記録データ取得完了: {len(df)}件")
            return df

        except Exception as e:
            logger.error(f"掃除記録データ取得エラー: {e}")
            st.error(f"掃除記録データ取得エラー: {e}")
            return pd.DataFrame(columns=["日時", "掃除種別", "記録者", "備考"])

    @st.cache_data(ttl=AppConfig.AUTO_REFRESH_INTERVAL)
    def get_cleaning_settings(_self) -> pd.DataFrame:
        """掃除種別設定データを取得"""
        try:
            sheet = _self.spreadsheet.worksheet(AppConfig.CLEANING_SETTINGS_SHEET)
            settings = sheet.get_all_records()

            if not settings:
                return pd.DataFrame(columns=["掃除種別", "推奨頻度（日）", "最終実施日", "次回予定日", "優先度"])

            df = pd.DataFrame(settings)

            # 日時列を datetime型に変換
            for col in ["最終実施日", "次回予定日"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            logger.info(f"掃除種別設定データ取得完了: {len(df)}件")
            return df

        except Exception as e:
            logger.error(f"掃除種別設定データ取得エラー: {e}")
            st.error(f"掃除種別設定データ取得エラー: {e}")
            return pd.DataFrame(columns=["掃除種別", "推奨頻度（日）", "最終実施日", "次回予定日", "優先度"])

    def get_contribution_calendar_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Contribution Calendar用のデータを生成"""
        records_df = self.get_cleaning_records()

        if records_df.empty:
            return pd.DataFrame()

        # 指定期間でフィルタリング
        mask = (records_df["日時"] >= start_date) & (records_df["日時"] <= end_date)
        filtered_records = records_df[mask]

        # 日付別の掃除回数を集計
        daily_counts = filtered_records.groupby(filtered_records["日時"].dt.date).size().reset_index()
        daily_counts.columns = ["date", "count"]

        # 全日付の範囲を作成
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        full_range = pd.DataFrame({"date": date_range.date})

        # 結合してない日は0で埋める
        result = full_range.merge(daily_counts, on="date", how="left")
        result["count"] = result["count"].fillna(0)

        return result

    def get_overdue_cleanings(self) -> List[Dict]:
        """期限切れの掃除一覧を取得"""
        settings_df = self.get_cleaning_settings()

        if settings_df.empty:
            return []

        overdue_list = []
        today = datetime.now()

        for _, row in settings_df.iterrows():
            last_date = row["最終実施日"]
            frequency = row["推奨頻度（日）"]
            cleaning_type = row["掃除種別"]
            priority = row["優先度"]

            if pd.isna(last_date):
                # 最終実施日がない場合は未実施とし、次回実施予定日は今日とする
                next_due_date = today
                days_until_due = 0
            else:
                next_due_date = last_date + timedelta(days=frequency)
                days_until_due = (next_due_date - today).days

            # 期限切れ（次回実施予定日が過ぎている）もしくは未実施の場合のみ追加
            if days_until_due <= 0 or pd.isna(last_date):
                overdue_list.append(
                    {
                        "掃除種別": cleaning_type,
                        "前回実施日": last_date if not pd.isna(last_date) else "未実施",
                        "次回実施予定日": next_due_date.strftime("%Y-%m-%d"),
                        "次回実施予定日までの日数": days_until_due,
                        "優先度": priority,
                    }
                )

        # 次回実施予定日までの日数（昇順）、優先度（高→中→低）でソート
        priority_order = {"高": 0, "中": 1, "低": 2}
        overdue_list.sort(key=lambda x: (x["次回実施予定日までの日数"], priority_order.get(x["優先度"], 3)))

        return overdue_list

    def get_cleaning_stats(self) -> Dict:
        """掃除統計データを取得"""
        records_df = self.get_cleaning_records()

        if records_df.empty:
            return {"total_cleanings": 0, "this_week": 0, "this_month": 0, "overdue_count": 0}

        today = datetime.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        stats = {
            "total_cleanings": len(records_df),
            "this_week": len(records_df[records_df["日時"] >= week_ago]),
            "this_month": len(records_df[records_df["日時"] >= month_ago]),
            "overdue_count": len(self.get_overdue_cleanings()),
        }

        return stats
