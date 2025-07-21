"""
データ可視化モジュール

掃除管理データを視覚化するためのコンポーネントを提供します。
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from .data_manager import DataManager


class CleaningVisualizer:
    """掃除データ可視化クラス"""

    def __init__(self, data_manager: DataManager):
        """可視化クラスを初期化"""
        self.data_manager = data_manager

    def render_contribution_calendar(self, start_date: datetime, end_date: datetime) -> None:
        """GitHub風のContribution Calendarを描画"""
        st.subheader("📅 掃除実施履歴 (Contribution Calendar)")

        # データを取得
        calendar_data = self.data_manager.get_contribution_calendar_data(start_date, end_date)

        if calendar_data.empty:
            st.info("表示期間内に掃除記録がありません")
            return

        # 週ごとにデータを整理
        calendar_data["date"] = pd.to_datetime(calendar_data["date"])
        calendar_data["week"] = calendar_data["date"].dt.isocalendar().week
        calendar_data["weekday"] = calendar_data["date"].dt.weekday
        calendar_data["year"] = calendar_data["date"].dt.year

        # ヒートマップ用のデータを作成
        weeks = []
        for year in calendar_data["year"].unique():
            year_data = calendar_data[calendar_data["year"] == year]
            for week in sorted(year_data["week"].unique()):
                week_data = year_data[year_data["week"] == week]
                week_counts = [0] * 7  # 月曜日から日曜日
                for _, row in week_data.iterrows():
                    week_counts[row["weekday"]] = row["count"]
                weeks.append(week_counts)

        if not weeks:
            st.info("表示期間内に掃除記録がありません")
            return

        # ヒートマップを作成
        weeks_array = np.array(weeks).T
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]

        fig = go.Figure(
            data=go.Heatmap(
                z=weeks_array,
                y=weekdays,
                colorscale="Greens",
                showscale=True,
                colorbar=dict(title="掃除回数"),
                hovertemplate="<b>%{y}</b><br>掃除回数: %{z}<extra></extra>",
            )
        )

        fig.update_layout(
            title="掃除実施履歴",
            xaxis_title="週",
            yaxis_title="曜日",
            height=300,
            xaxis=dict(showticklabels=False),
            yaxis=dict(autorange="reversed"),
            # モバイル対応設定
            font=dict(size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            showlegend=False,
        )

        # モバイル対応設定
        config = {
            "displayModeBar": True,
            "displaylogo": False,
            "responsive": True,
            "modeBarButtonsToRemove": [
                "pan2d",
                "lasso2d",
                "select2d",
                "autoScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "toggleSpikelines",
            ],
        }

        st.plotly_chart(fig, use_container_width=True, config=config)

        # 統計情報を表示
        total_days = len(calendar_data)
        active_days = len(calendar_data[calendar_data["count"] > 0])
        max_cleanings = calendar_data["count"].max()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("対象期間", f"{total_days}日")
        with col2:
            st.metric("掃除実施日", f"{active_days}日 ({active_days/total_days*100:.1f}%)")
        with col3:
            st.metric("最大掃除回数/日", f"{max_cleanings}回")

    def render_overdue_status(self) -> None:
        """期限切れ状況を表示"""
        st.subheader("⚠️ 期限切れ状況")

        overdue_cleanings = self.data_manager.get_overdue_cleanings()

        if not overdue_cleanings:
            st.success("🎉 期限切れの掃除はありません！")
            return

        # データフレームに変換
        overdue_df = pd.DataFrame(overdue_cleanings)

        # 前回実施日の表示形式を調整
        if not overdue_df.empty:
            overdue_df["前回実施日"] = overdue_df["前回実施日"].apply(
                lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) and x != "未実施" else "未実施"
            )

        # 表形式で表示
        st.dataframe(
            overdue_df,
            use_container_width=True,
            column_config={
                "掃除種別": {"width": 150},
                "前回実施日": {"width": 120},
                "次回実施予定日": {"width": 120},
                "次回実施予定日までの日数": {"width": 100},
                "優先度": {"width": 80},
            },
        )

    def render_dashboard_metrics(self) -> None:
        """ダッシュボードメトリクスを表示"""
        stats = self.data_manager.get_cleaning_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("総掃除回数", stats["total_cleanings"], delta=None)

        with col2:
            st.metric("今週の掃除", stats["this_week"], delta=None)

        with col3:
            st.metric("今月の掃除", stats["this_month"], delta=None)

        with col4:
            delta_color = "inverse" if stats["overdue_count"] > 0 else "normal"
            st.metric("期限切れ", stats["overdue_count"], delta=None, delta_color=delta_color)

    def render_recent_cleanings(self, limit: int = 10) -> None:
        """最近の掃除記録を表示"""
        st.subheader("🕐 最近の掃除記録")

        records_df = self.data_manager.get_cleaning_records()

        if records_df.empty:
            st.info("掃除記録がありません")
            return

        recent_records = records_df.head(limit)

        # 表示用にデータを整形
        display_records = recent_records.copy()
        if "日時" in display_records.columns:
            display_records["日時"] = display_records["日時"].dt.strftime("%Y-%m-%d %H:%M")

        st.dataframe(display_records, use_container_width=True)
