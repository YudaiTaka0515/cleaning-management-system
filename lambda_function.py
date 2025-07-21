"""
音声ベース掃除記録システム - メインLambda関数

Amazon Alexa Skills Kitを使用した音声ベース掃除記録システムのメイン関数です。
Googleスプレッドシートに掃除記録を保存し、期限切れの掃除を自動リマインドします。

主な機能:
- 音声による掃除記録（「トイレ掃除をしました」）
- 期限切れ掃除の自動リマインド
- 掃除状況の確認
- Googleスプレッドシートとの連携

対応する掃除種別:
- トイレ掃除（3日周期、高優先度）
- 風呂掃除（7日周期、高優先度）
- キッチン掃除（3日周期、高優先度）
- 床掃除（7日周期、中優先度）
- 窓掃除（14日周期、低優先度）
- 掃除機かけ（3日周期、中優先度）
"""

import logging
import os
import sys
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# CloudWatch Logsへの確実な出力のためのログ設定
# ストリームハンドラーを明示的に追加
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 既存ハンドラーをクリア
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# CloudWatch用のストリームハンドラーを追加
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)

logger = logging.getLogger(__name__)

# 起動時のログ出力
logger.info("🚀 Lambda関数モジュール読み込み開始")

# ローカルモジュールのインポート
try:
    from src.alexa_handlers import (
        LaunchRequestHandler,
        RecordCleaningIntentHandler,
        CheckCleaningStatusIntentHandler,
        HelpIntentHandler,
        CancelOrStopIntentHandler,
        FallbackIntentHandler,
        SessionEndedRequestHandler,
    )

    logger.info("✅ Alexaハンドラーのインポート成功")
except Exception as e:
    logger.error(f"❌ Alexaハンドラーのインポートエラー: {e}")
    raise

# スキルビルダーの作成
sb = SkillBuilder()
logger.info("✅ SkillBuilder作成完了")


class GlobalExceptionHandler(AbstractExceptionHandler):
    """グローバル例外ハンドラー"""

    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.error(f"❌ グローバル例外: {exception}")
        logger.error(f"❌ 例外タイプ: {type(exception).__name__}")

        # スタックトレースも出力
        import traceback

        logger.error(f"❌ スタックトレース: {traceback.format_exc()}")

        speech_text = "申し訳ございません。システムエラーが発生しました。しばらく経ってから再度お試しください。"

        return handler_input.response_builder.speak(speech_text).response


# ハンドラーの登録
try:
    sb.add_request_handler(LaunchRequestHandler())
    sb.add_request_handler(RecordCleaningIntentHandler())
    sb.add_request_handler(CheckCleaningStatusIntentHandler())
    sb.add_request_handler(HelpIntentHandler())
    sb.add_request_handler(CancelOrStopIntentHandler())
    sb.add_request_handler(FallbackIntentHandler())
    sb.add_request_handler(SessionEndedRequestHandler())
    logger.info("✅ リクエストハンドラー登録完了")
except Exception as e:
    logger.error(f"❌ ハンドラー登録エラー: {e}")
    raise

# 例外ハンドラーの登録
try:
    sb.add_exception_handler(GlobalExceptionHandler())
    logger.info("✅ 例外ハンドラー登録完了")
except Exception as e:
    logger.error(f"❌ 例外ハンドラー登録エラー: {e}")
    raise

# Lambda関数のハンドラー
try:
    lambda_handler = sb.lambda_handler()
    logger.info("✅ Lambda関数ハンドラー作成完了")
except Exception as e:
    logger.error(f"❌ Lambda関数ハンドラー作成エラー: {e}")
    raise


def lambda_handler_wrapper(event, context):
    """
    AWS Lambda関数のエントリーポイント

    Args:
        event: Alexaからのリクエストイベント
        context: Lambda実行コンテキスト

    Returns:
        Alexaへのレスポンス
    """
    # 関数開始時のログ
    logger.info("=" * 50)
    logger.info("🎯 Lambda関数実行開始")
    logger.info(f"📥 リクエストID: {context.aws_request_id}")
    logger.info(f"📥 関数名: {context.function_name}")
    logger.info(f"📥 実行時間制限: {context.get_remaining_time_in_millis()}ms")

    try:
        # イベントの詳細情報をログ出力
        request_type = event.get("request", {}).get("type", "Unknown")
        logger.info(f"📥 リクエストタイプ: {request_type}")

        # セッション情報も記録
        session_id = event.get("session", {}).get("sessionId", "Unknown")
        logger.info(f"📥 セッションID: {session_id}")

        # 詳細なイベント情報（機密情報は除く）
        safe_event = {
            "version": event.get("version"),
            "session": {
                "new": event.get("session", {}).get("new"),
                "sessionId": event.get("session", {}).get("sessionId"),
                "application": event.get("session", {}).get("application"),
            },
            "request": event.get("request", {}),
        }
        logger.info(f"📥 イベント詳細: {safe_event}")

        # 環境変数の確認
        logger.info("🔍 環境変数チェック開始")
        required_env_vars = ["GOOGLE_SERVICE_ACCOUNT_KEY", "GOOGLE_SPREADSHEET_ID"]
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

        if missing_vars:
            logger.error(f"❌ 必要な環境変数が設定されていません: {missing_vars}")
            raise ValueError(f"Missing environment variables: {missing_vars}")

        logger.info("✅ 環境変数チェック完了")
        logger.info(f"📋 スプレッドシートID: {os.environ.get('GOOGLE_SPREADSHEET_ID')}")

        # Google Sheets接続のテスト
        logger.info("📚 Google Sheets接続テスト開始")
        try:
            from src.google_sheets_manager import GoogleSheetsManager

            logger.info("✅ GoogleSheetsManagerのインポート成功")

            # 簡単な接続テスト
            GoogleSheetsManager()  # インスタンス化のテストのみ
            logger.info("✅ GoogleSheetsManager初期化成功")

        except Exception as sheets_error:
            logger.error(f"❌ Google Sheets接続エラー: {sheets_error}")
            logger.error(f"❌ エラータイプ: {type(sheets_error).__name__}")

            # 詳細なスタックトレース
            import traceback

            logger.error(f"❌ Google Sheets詳細エラー: {traceback.format_exc()}")
            raise

        # スキルハンドラーを実行
        logger.info("🎯 スキルハンドラー実行開始")
        response = lambda_handler(event, context)
        logger.info("✅ スキルハンドラー実行完了")

        # レスポンス情報をログ出力（機密情報は除く）
        safe_response = {
            "version": response.get("version"),
            "response": {
                "outputSpeech": response.get("response", {}).get("outputSpeech", {}).get("type"),
                "shouldEndSession": response.get("response", {}).get("shouldEndSession"),
            },
        }
        logger.info(f"📤 レスポンス概要: {safe_response}")

        logger.info("✅ Lambda関数正常終了")
        logger.info("=" * 50)
        return response

    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"❌ Lambda関数エラー: {e}")
        logger.error(f"❌ エラータイプ: {type(e).__name__}")
        logger.error(f"❌ エラー詳細: {str(e)}")

        # スタックトレースもログに出力
        import traceback

        logger.error(f"❌ スタックトレース: {traceback.format_exc()}")

        # エラー時のフォールバック応答
        fallback_response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": f"申し訳ございません。システムエラーが発生しました。エラータイプ: {type(e).__name__}",
                },
                "shouldEndSession": True,
            },
        }
        logger.error(f"📤 フォールバックレスポンス: {fallback_response}")
        logger.error("=" * 50)
        return fallback_response

    finally:
        # 実行終了時の情報
        logger.info(f"⏰ 実行終了時点の残り時間: {context.get_remaining_time_in_millis()}ms")


# 直接実行時のテスト用
if __name__ == "__main__":
    logger.info("🧪 テスト実行モード")

    # テスト用のイベントデータ
    test_event = {
        "version": "1.0",
        "session": {
            "new": True,
            "sessionId": "test-session",
            "application": {"applicationId": "test-app"},
            "user": {"userId": "test-user"},
        },
        "request": {"type": "LaunchRequest", "requestId": "test-request", "timestamp": "2024-01-01T00:00:00Z"},
    }

    test_context = type(
        "Context",
        (),
        {
            "function_name": "test-function",
            "aws_request_id": "test-request-id",
            "get_remaining_time_in_millis": lambda: 30000,
        },
    )()

    logger.info("🧪 テスト実行中...")
    result = lambda_handler_wrapper(test_event, test_context)
    logger.info(f"📤 テスト結果: {result}")

logger.info("🏁 Lambda関数モジュール読み込み完了")
