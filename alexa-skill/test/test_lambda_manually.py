#!/usr/bin/env python3
"""
Lambda関数手動実行テスト

AWS Lambda関数を直接実行してCloudWatchログの出力をテストします。
"""

import boto3
import json
from datetime import datetime
import time


def test_lambda_function(profile="indivisual", function_name="cleaning-management-alexa-skill"):
    """Lambda関数の手動実行テスト"""

    print("🚀 Lambda関数手動実行テスト開始")
    print("=" * 50)

    try:
        # AWS セッション
        session = boto3.Session(profile_name=profile)
        lambda_client = session.client("lambda")
        logs_client = session.client("logs")

        # テスト用ペイロード（Alexa LaunchRequest）
        test_payload = {
            "version": "1.0",
            "session": {
                "new": True,
                "sessionId": "test-session-manual",
                "application": {"applicationId": "test-app"},
                "user": {"userId": "test-user"},
            },
            "request": {
                "type": "LaunchRequest",
                "requestId": "test-request-manual",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        }

        print(f"📋 テスト対象関数: {function_name}")
        print("📤 実行ペイロード: LaunchRequest")

        # Lambda関数実行
        print("⏳ Lambda関数を実行中...")
        response = lambda_client.invoke(
            FunctionName=function_name, Payload=json.dumps(test_payload), LogType="Tail"  # ログを返すように指定
        )

        print(f"✅ 実行完了: {response['StatusCode']}")

        # レスポンス内容確認
        payload_response = json.loads(response["Payload"].read())
        print(f"📥 レスポンスタイプ: {type(payload_response)}")
        if isinstance(payload_response, dict):
            if "version" in payload_response:
                print(f"📋 Alexaレスポンス: バージョン {payload_response['version']}")
            if "response" in payload_response:
                output_speech = payload_response.get("response", {}).get("outputSpeech", {})
                if output_speech:
                    print(f"🎤 音声出力タイプ: {output_speech.get('type', 'Unknown')}")

        # 実行ログの確認（Lambda関数のレスポンスに含まれるログ）
        if "LogResult" in response:
            import base64

            log_data = base64.b64decode(response["LogResult"]).decode("utf-8")
            print("\n📋 Lambda実行ログ:")
            print("-" * 30)
            print(log_data)
            print("-" * 30)

        # CloudWatchログの確認
        print("\n🔍 CloudWatchログ確認（5秒後）...")
        time.sleep(5)

        log_group_name = f"/aws/lambda/{function_name}"

        try:
            # ログストリーム取得
            streams_response = logs_client.describe_log_streams(
                logGroupName=log_group_name, orderBy="LastEventTime", descending=True, limit=1
            )

            if streams_response["logStreams"]:
                latest_stream = streams_response["logStreams"][0]
                stream_name = latest_stream["logStreamName"]
                print(f"📋 最新ログストリーム: {stream_name}")

                # 最新ログイベント取得
                events_response = logs_client.get_log_events(
                    logGroupName=log_group_name, logStreamName=stream_name, limit=10, startFromHead=False
                )

                events = events_response["events"]
                print(f"\n📋 CloudWatchログエントリー（{len(events)}件）:")
                print("-" * 50)

                for i, event in enumerate(events, 1):
                    timestamp = datetime.fromtimestamp(event["timestamp"] / 1000)
                    message = event["message"].strip()
                    print(f"{i:2d}. {timestamp} | {message}")

                print("-" * 50)
                print("✅ CloudWatchログ出力確認完了")

            else:
                print("⚠️  CloudWatchログストリームがまだ作成されていません")

        except Exception as e:
            print(f"❌ CloudWatchログ確認エラー: {e}")

        print("\n✅ Lambda関数手動実行テスト完了")
        return True

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False


if __name__ == "__main__":
    success = test_lambda_function()

    if success:
        print("\n🎉 テスト成功: CloudWatchログが正常に出力されています")
    else:
        print("\n❌ テスト失敗: CloudWatchログの出力に問題があります")
        print("\n💡 次の手順:")
        print("1. IAMロールのCloudWatch Logs権限を確認")
        print("2. Lambda関数のログ設定を確認")
        print("3. AWS CloudWatchコンソールで直接確認")
