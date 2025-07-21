"""
メインアプリケーションファイル

掃除管理システムの可視化ダッシュボードのエントリーポイント
"""

import streamlit as st
from datetime import datetime, timedelta
import logging

from .config import validate_config, ValidationError
from .data_manager import DataManager
from .visualization import CleaningVisualizer
from .mobile_fixes import apply_mobile_styles, add_error_handling_js, check_device_compatibility


# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_app():
    """アプリケーションを初期化"""
    try:
        # 設定検証
        validate_config()

        # データマネージャーとビジュアライザーを初期化
        if "data_manager" not in st.session_state:
            st.session_state.data_manager = DataManager()

        if "visualizer" not in st.session_state:
            st.session_state.visualizer = CleaningVisualizer(st.session_state.data_manager)

        return True

    except ValidationError as e:
        st.error(f"設定エラー: {e}")
        st.info("環境変数 GOOGLE_SERVICE_ACCOUNT_KEY と GOOGLE_SPREADSHEET_ID を設定してください")
        return False
    except Exception as e:
        st.error(f"初期化エラー: {e}")
        logger.error(f"初期化エラー: {e}")
        return False


def main():
    """メイン関数"""
    # ページ設定
    st.set_page_config(
        page_title="掃除管理ダッシュボード",
        page_icon="🧹",
        layout="wide",
        initial_sidebar_state="auto",  # モバイル対応のため自動調整
    )

    # モバイル/タブレット対応
    apply_mobile_styles()
    add_error_handling_js()
    check_device_compatibility()

    # アプリケーション初期化
    if not initialize_app():
        return

    st.title("🧹 掃除管理ダッシュボード")

    visualizer = st.session_state.visualizer

    # 1. 統計メトリクス
    st.subheader("📊 概要")
    visualizer.render_dashboard_metrics()

    # 4. 期限切れ掃除警告
    st.markdown("---")
    visualizer.render_overdue_status()

    # 2. Contribution Calendar
    st.markdown("---")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    visualizer.render_contribution_calendar(start_date, end_date)

    # 3. 最近の掃除記録
    st.markdown("---")
    visualizer.render_recent_cleanings(limit=10)


if __name__ == "__main__":
    main()
