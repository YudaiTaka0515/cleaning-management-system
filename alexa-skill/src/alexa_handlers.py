"""
Alexa Skills Kitハンドラーモジュール

音声コマンドを処理するためのハンドラークラスを提供します。
起動、掃除記録、状況確認、ヘルプ、終了などの機能を含みます。
"""

import logging
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

from .google_sheets_manager import GoogleSheetsManager

logger = logging.getLogger(__name__)


class LaunchRequestHandler(AbstractRequestHandler):
    """起動時のハンドラー"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        try:
            logger.info("🚀 掃除管理スキル起動")

            # 期限切れの掃除をチェック
            sheets_manager = GoogleSheetsManager()
            overdue_cleanings = sheets_manager.get_overdue_cleanings()

            if overdue_cleanings:
                # 期限切れがある場合
                overdue_count = len(overdue_cleanings)
                speech_text = f"掃除管理システムを開始します。現在、{overdue_count}件の掃除が期限切れです。"
                speech_text += " 掃除をした場合は「トイレ掃除をしました」のように話しかけてください。"

            else:
                # 期限切れがない場合
                speech_text = (
                    "掃除管理システムを開始します。現在、期限切れの掃除はありません。素晴らしいですね！ "
                    "掃除をした場合は「トイレ掃除をしました」のように話しかけてください。"
                )

            logger.info(f"✅ 起動応答: 期限切れ{len(overdue_cleanings)}件")

            return (
                handler_input.response_builder.speak(speech_text)
                .set_card(SimpleCard("掃除管理システム", speech_text))
                .set_should_end_session(False)
                .response
            )

        except Exception as e:
            logger.error(f"❌ 起動ハンドラーエラー: {e}")
            error_speech = "申し訳ございません。システムの初期化中にエラーが発生しました。"
            return handler_input.response_builder.speak(error_speech).response


class RecordCleaningIntentHandler(AbstractRequestHandler):
    """掃除記録のハンドラー"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("RecordCleaningIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        try:
            logger.info("📝 掃除記録処理開始")

            # スロットから掃除種別を取得
            slots = handler_input.request_envelope.request.intent.slots
            cleaning_type_slot = slots.get("CleaningType")

            if not cleaning_type_slot or not cleaning_type_slot.value:
                speech_text = "掃除の種類が聞き取れませんでした。もう一度お話しください。"
                return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response

            cleaning_type = cleaning_type_slot.value
            logger.info(f"🎯 掃除種別: {cleaning_type}")

            # Google Sheetsに記録
            sheets_manager = GoogleSheetsManager()
            success = sheets_manager.add_cleaning_record(cleaning_type)

            if success:
                speech_text = f"{cleaning_type}の記録を保存しました。お疲れさまでした！"
                logger.info(f"✅ 掃除記録成功: {cleaning_type}")
            else:
                speech_text = "記録の保存中にエラーが発生しました。もう一度お試しください。"
                logger.error(f"❌ 掃除記録失敗: {cleaning_type}")

            return (
                handler_input.response_builder.speak(speech_text)
                .set_card(SimpleCard("掃除記録", speech_text))
                .set_should_end_session(True)
                .response
            )

        except Exception as e:
            logger.error(f"❌ 掃除記録ハンドラーエラー: {e}")
            error_speech = "申し訳ございません。掃除記録中にエラーが発生しました。"
            return handler_input.response_builder.speak(error_speech).response


class CheckCleaningStatusIntentHandler(AbstractRequestHandler):
    """掃除状況確認のハンドラー"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("CheckCleaningStatusIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        try:
            logger.info("📊 掃除状況確認処理開始")

            sheets_manager = GoogleSheetsManager()
            overdue_cleanings = sheets_manager.get_overdue_cleanings()

            if not overdue_cleanings:
                speech_text = "素晴らしいです！現在、期限切れの掃除はありません。"
            else:
                overdue_count = len(overdue_cleanings)
                speech_text = f"現在、{overdue_count}件の掃除が期限切れです。"

                # 上位5件を詳細に報告
                top_overdue = overdue_cleanings[:5]
                details = []
                for item in top_overdue:
                    days = item["days_overdue"]
                    priority = item["priority"]
                    if days == 0:
                        details.append(f"{item['type']}（本日が期限、優先度{priority}）")
                    else:
                        details.append(f"{item['type']}（{days}日遅れ、優先度{priority}）")

                speech_text += " 詳細は、" + "、".join(details)
                if len(overdue_cleanings) > 5:
                    speech_text += f"、他{len(overdue_cleanings) - 5}件"
                speech_text += "です。"

            logger.info(f"✅ 状況確認応答: 期限切れ{len(overdue_cleanings)}件")

            return (
                handler_input.response_builder.speak(speech_text)
                .set_card(SimpleCard("掃除状況", speech_text))
                .set_should_end_session(True)
                .response
            )

        except Exception as e:
            logger.error(f"❌ 状況確認ハンドラーエラー: {e}")
            error_speech = "申し訳ございません。状況確認中にエラーが発生しました。"
            return handler_input.response_builder.speak(error_speech).response


class HelpIntentHandler(AbstractRequestHandler):
    """ヘルプのハンドラー"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = (
            "掃除管理システムです。掃除をした時は「トイレ掃除をしました」のように話しかけてください。"
            "掃除の状況を知りたい時は「掃除の状況を教えて」と言ってください。"
            "対応している掃除種別は、トイレ掃除、風呂掃除、キッチン掃除、床掃除、窓掃除、掃除機かけです。"
        )

        return (
            handler_input.response_builder.speak(speech_text)
            .set_card(SimpleCard("ヘルプ", speech_text))
            .set_should_end_session(False)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """キャンセル・停止のハンドラー"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(
            handler_input
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = "掃除管理システムを終了します。お疲れさまでした！"

        return handler_input.response_builder.speak(speech_text).set_card(SimpleCard("終了", speech_text)).response


class FallbackIntentHandler(AbstractRequestHandler):
    """フォールバックのハンドラー"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = (
            "すみません、よく分かりませんでした。"
            "掃除をした時は「トイレ掃除をしました」のように話しかけてください。"
            "ヘルプが必要な場合は「ヘルプ」と言ってください。"
        )

        return (
            handler_input.response_builder.speak(speech_text)
            .set_card(SimpleCard("理解できませんでした", speech_text))
            .set_should_end_session(False)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """セッション終了のハンドラー"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        logger.info("🔚 セッション終了")
        return handler_input.response_builder.response


class CatchAllExceptionHandler:
    """全例外をキャッチするハンドラー"""

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(f"❌ 予期しないエラー: {exception}")
        speech_text = "申し訳ございません。予期しないエラーが発生しました。"

        return handler_input.response_builder.speak(speech_text).set_card(SimpleCard("エラー", speech_text)).response
