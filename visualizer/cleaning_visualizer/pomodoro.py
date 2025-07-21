"""
ポモドーロタイマーモジュール

掃除作業時に使用するポモドーロタイマー機能を提供します。
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional

from .config import AppConfig


class PomodoroTimer:
    """ポモドーロタイマークラス"""

    def __init__(self):
        """ポモドーロタイマーを初期化"""
        self.config = AppConfig.POMODORO_CONFIG
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """セッション状態を初期化"""
        if "pomodoro_state" not in st.session_state:
            st.session_state.pomodoro_state = {
                "is_running": False,
                "current_phase": "work",  # work, short_break, long_break
                "start_time": None,
                "end_time": None,
                "pomodoro_count": 0,
                "completed_pomodoros": 0,
            }

    def get_phase_duration(self, phase: str) -> int:
        """フェーズの時間を取得（分）"""
        durations = {
            "work": self.config["work_time"],
            "short_break": self.config["short_break"],
            "long_break": self.config["long_break"],
        }
        return durations.get(phase, 25)

    def start_timer(self, phase: str = "work") -> None:
        """タイマーを開始"""
        duration = self.get_phase_duration(phase)
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration)

        st.session_state.pomodoro_state.update(
            {"is_running": True, "current_phase": phase, "start_time": start_time, "end_time": end_time}
        )

    def stop_timer(self) -> None:
        """タイマーを停止"""
        st.session_state.pomodoro_state.update({"is_running": False, "start_time": None, "end_time": None})

    def complete_pomodoro(self) -> None:
        """ポモドーロを完了"""
        state = st.session_state.pomodoro_state

        if state["current_phase"] == "work":
            state["completed_pomodoros"] += 1
            state["pomodoro_count"] = (state["pomodoro_count"] + 1) % self.config["long_break_after"]

            # 次のフェーズを決定
            if state["pomodoro_count"] == 0:
                next_phase = "long_break"
            else:
                next_phase = "short_break"

            self.start_timer(next_phase)
        else:
            # 休憩終了後は作業に戻る
            self.start_timer("work")

    def get_remaining_time(self) -> Optional[timedelta]:
        """残り時間を取得"""
        state = st.session_state.pomodoro_state

        if not state["is_running"] or not state["end_time"]:
            return None

        now = datetime.now()
        if now >= state["end_time"]:
            return timedelta(0)

        return state["end_time"] - now

    def is_time_up(self) -> bool:
        """時間切れかどうかチェック"""
        remaining = self.get_remaining_time()
        return remaining is not None and remaining.total_seconds() <= 0

    def get_phase_emoji(self, phase: str) -> str:
        """フェーズの絵文字を取得"""
        emojis = {"work": "🍅", "short_break": "☕", "long_break": "🌟"}
        return emojis.get(phase, "⏰")

    def get_phase_name(self, phase: str) -> str:
        """フェーズの日本語名を取得"""
        names = {"work": "作業時間", "short_break": "短い休憩", "long_break": "長い休憩"}
        return names.get(phase, "不明")

    def format_time(self, td: timedelta) -> str:
        """時間を MM:SS 形式でフォーマット"""
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def render_timer(self) -> None:
        """タイマーUIを描画"""
        state = st.session_state.pomodoro_state

        st.subheader("🍅 ポモドーロタイマー")

        # 統計情報
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("完了ポモドーロ", state["completed_pomodoros"])
        with col2:
            current_cycle = state["pomodoro_count"]
            st.metric("現在のサイクル", f"{current_cycle}/{self.config['long_break_after']}")
        with col3:
            next_break = "長い休憩" if state["pomodoro_count"] == self.config["long_break_after"] - 1 else "短い休憩"
            st.metric("次の休憩", next_break)

        # 現在の状態
        if state["is_running"]:
            current_phase = state["current_phase"]
            phase_emoji = self.get_phase_emoji(current_phase)
            phase_name = self.get_phase_name(current_phase)

            st.markdown(f"### {phase_emoji} {phase_name}")

            remaining = self.get_remaining_time()
            if remaining:
                if self.is_time_up():
                    st.success("⏰ 時間です！")
                    st.balloons()

                    # 自動的に次のフェーズに移行
                    if st.button("次のフェーズに進む"):
                        self.complete_pomodoro()
                        st.rerun()
                else:
                    # 残り時間を大きく表示
                    time_str = self.format_time(remaining)
                    st.markdown(f"## ⏱️ {time_str}")

                    # プログレスバー
                    duration = self.get_phase_duration(current_phase) * 60
                    elapsed = duration - remaining.total_seconds()
                    progress = elapsed / duration
                    st.progress(progress)

                    # 停止ボタン
                    if st.button("⏹️ 停止"):
                        self.stop_timer()
                        st.rerun()
        else:
            st.markdown("### タイマーが停止中です")

            # 開始オプション
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🍅 作業開始"):
                    self.start_timer("work")
                    st.rerun()

            with col2:
                if st.button("☕ 短い休憩"):
                    self.start_timer("short_break")
                    st.rerun()

            with col3:
                if st.button("🌟 長い休憩"):
                    self.start_timer("long_break")
                    st.rerun()

        # 設定表示
        with st.expander("⚙️ 設定"):
            st.write(f"**作業時間:** {self.config['work_time']}分")
            st.write(f"**短い休憩:** {self.config['short_break']}分")
            st.write(f"**長い休憩:** {self.config['long_break']}分")
            st.write(f"**長い休憩の間隔:** {self.config['long_break_after']}ポモドーロ")

    def render_compact_timer(self) -> None:
        """コンパクトなタイマーUIを描画"""
        state = st.session_state.pomodoro_state

        if state["is_running"]:
            remaining = self.get_remaining_time()
            if remaining:
                phase_emoji = self.get_phase_emoji(state["current_phase"])
                if self.is_time_up():
                    st.error(f"{phase_emoji} 時間です！")
                else:
                    time_str = self.format_time(remaining)
                    st.info(f"{phase_emoji} {time_str}")
        else:
            st.info("🍅 ポモドーロタイマー停止中")
