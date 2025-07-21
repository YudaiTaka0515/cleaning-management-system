#!/usr/bin/env python3
"""
Google Sheets作成・書き込みテスト

Google Sheetsの作成と書き込み処理を詳細にテストし、
問題箇所を特定します。
"""

import boto3
import json
from datetime import datetime


def test_sheets_creation():
    """Google Sheetsの作成と書き込みをテスト"""

    print("🧪 Google Sheets作成・書き込みテスト開始")
    print("=" * 60)

    # Lambda関数を実行してより詳細なログを取得
    try:
        session = boto3.Session(profile_name="indivisual")
        lambda_client = session.client("lambda")

        # テスト用ペイロード
        test_payload = {
            "version": "1.0",
            "session": {
                "new": True,
                "sessionId": "test-session-sheets",
                "application": {"applicationId": "test-app"},
                "user": {"userId": "test-user"},
            },
            "request": {
                "type": "LaunchRequest",
                "requestId": "test-request-sheets",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        }

        print("📤 Lambda関数を実行中...")
        response = lambda_client.invoke(
            FunctionName="cleaning-management-alexa-skill", Payload=json.dumps(test_payload), LogType="Tail"
        )

        print(f"✅ 実行完了: {response['StatusCode']}")

        # 実行ログの詳細確認
        if "LogResult" in response:
            import base64

            log_data = base64.b64decode(response["LogResult"]).decode("utf-8")
            print("\n📋 詳細実行ログ:")
            print("-" * 60)
            print(log_data)
            print("-" * 60)

        # CloudWatchから最新ログを取得
        logs_client = session.client("logs")

        print("\n🔍 CloudWatchログ詳細確認...")

        try:
            # 最新のログストリーム取得
            streams_response = logs_client.describe_log_streams(
                logGroupName="/aws/lambda/cleaning-management-alexa-skill",
                orderBy="LastEventTime",
                descending=True,
                limit=1,
            )

            if streams_response["logStreams"]:
                latest_stream = streams_response["logStreams"][0]
                stream_name = latest_stream["logStreamName"]

                # 詳細ログイベント取得（より多くの件数）
                events_response = logs_client.get_log_events(
                    logGroupName="/aws/lambda/cleaning-management-alexa-skill",
                    logStreamName=stream_name,
                    limit=50,  # より多くのログを取得
                    startFromHead=False,
                )

                events = events_response["events"]
                print(f"\n📋 CloudWatch詳細ログ（{len(events)}件）:")
                print("-" * 80)

                # Google Sheets関連のログを特に注目
                sheets_logs = []
                error_logs = []

                for i, event in enumerate(events, 1):
                    timestamp = datetime.fromtimestamp(event["timestamp"] / 1000)
                    message = event["message"].strip()

                    print(f"{i:2d}. {timestamp} | {message}")

                    # Google Sheets関連のログを分類
                    if "google_sheets_manager" in message or "Google Sheets" in message:
                        sheets_logs.append(message)
                    if "ERROR" in message or "❌" in message:
                        error_logs.append(message)

                print("-" * 80)

                # 分析結果
                print("\n📊 ログ分析結果:")
                print(f"📋 Google Sheets関連ログ: {len(sheets_logs)}件")
                print(f"❌ エラーログ: {len(error_logs)}件")

                if sheets_logs:
                    print("\n📚 Google Sheets関連ログ詳細:")
                    for log in sheets_logs:
                        print(f"  • {log}")

                if error_logs:
                    print("\n❌ エラーログ詳細:")
                    for log in error_logs:
                        print(f"  • {log}")

                # 期待される処理が実行されているかチェック
                expected_processes = [
                    "Google Sheets初期化成功",
                    "掃除種別設定シートを新規作成中",
                    "デフォルト設定を書き込み中",
                    "掃除種別設定シート作成完了",
                ]

                print("\n🔍 期待される処理の確認:")
                for process in expected_processes:
                    found = any(process in log for log in sheets_logs)
                    status = "✅" if found else "❌"
                    print(f"  {status} {process}")

        except Exception as e:
            print(f"❌ CloudWatchログ取得エラー: {e}")

        # 次に実際のスプレッドシートの状態を確認するための情報
        print("\n💡 次のステップ:")
        print("1. Google Sheetsを直接確認")
        print("2. 掃除種別設定シートが存在するかチェック")
        print("3. シートの内容を確認")

        return True

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False


if __name__ == "__main__":
    success = test_sheets_creation()

    if success:
        print("\n🎯 テスト完了")
    else:
        print("\n❌ テスト失敗")
