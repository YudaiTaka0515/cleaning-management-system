# 音声ベース掃除記録システム開発ログ

## 要求事項
- 掃除の記録を音声ベースで行う
- 一定期間実施されていない掃除種別がある場合、音声でリマインドする

## 実装方針検討

### システム構成案（更新版）
1. **音声インターフェース**: Amazon Alexa Skills Kit (ASK)
2. **バックエンド**: AWS Lambda (Python)
3. **データ管理**: Googleスプレッドシート（コスト効率重視）
4. **リマインド機能**: CloudWatch Events + Lambda

### 必要な機能
1. **音声認識・対話機能**
   - 掃除完了の記録
   - 掃除履歴の確認
   - リマインド通知

2. **データ管理機能**
   - 掃除種別マスタ管理
   - 掃除実行履歴の記録
   - リマインド設定管理

3. **リマインド機能**
   - 定期的な実行状況チェック
   - 条件に基づいた音声通知

## 技術スタック（確定版）
- **音声**: Alexa Skills Kit
- **サーバー**: AWS Lambda (Python 3.9+)
- **データ**: Googleスプレッドシート + Google Sheets API
- **スケジューラー**: Amazon CloudWatch Events
- **パッケージ管理**: Poetry
- **ライブラリ**: gspread, boto3, ask-sdk

## コスト効率の利点
- Googleスプレッドシート: 無料
- Lambda: 低使用量なら実質無料
- DynamoDB不要でコスト削減

## 必要なGoogleスプレッドシート構成
1. **掃除記録シート**: 日付、掃除種別、実行者など
2. **掃除種別マスタ**: 掃除の種類、推奨頻度
3. **リマインド設定**: 各掃除の通知間隔

## 実装完了
### 2024年現在の進捗
- ✅ poetryを使ったプロジェクト設定完了
- ✅ Lambda関数（Python）の実装完了
- ✅ Google Sheets API連携実装完了
- ✅ Alexaスキルの対話モデル設計完了
- ✅ デプロイスクリプト作成完了
- ✅ ドキュメント作成完了

## 作成したファイル詳細

### 1. pyproject.toml
- Poetryによるパッケージ管理設定
- 本番・開発用依存関係の定義
- Python 3.9+対応
- 含まれるライブラリ:
  - gspread (Google Sheets API)
  - ask-sdk-core (Alexa SDK)
  - boto3 (AWS SDK)
  - google-auth (認証)

### 2. lambda_function.py
- メインのLambda関数ファイル
- Alexaスキルハンドラー実装:
  - LaunchRequestHandler: スキル起動時の処理
  - RecordCleaningIntentHandler: 掃除記録処理
  - CheckCleaningStatusIntentHandler: 掃除状況確認
  - HelpIntentHandler: ヘルプ機能
  - CancelOrStopIntentHandler: 終了処理
- CloudWatch Events対応:
  - 定期リマインダー処理
  - 期限切れ掃除のチェック

### 3. google_sheets_manager.py
- Googleスプレッドシート連携クラス
- 主要機能:
  - record_cleaning(): 掃除記録の追加
  - get_cleaning_history(): 掃除履歴の取得
  - get_cleaning_types_config(): 掃除種別設定管理
  - get_overdue_cleanings(): 期限切れ掃除の検出
  - get_cleaning_stats(): 掃除統計の取得
- デフォルト掃除種別:
  - トイレ掃除（3日周期）
  - 風呂掃除（2日周期）
  - キッチン掃除（1日周期）
  - 掃除機（7日周期）
  - 床拭き（7日周期）
  - 窓拭き（30日周期）

### 4. skill.json
- Alexaスキルの対話モデル定義
- 呼び出し名: 「掃除記録」
- インテント:
  - RecordCleaningIntent: 掃除記録用
  - CheckCleaningStatusIntent: 状況確認用
- スロット:
  - CleaningTypes: 掃除種別の定義
- サンプル発話:
  - 「トイレ掃除をしました」
  - 「掃除の状況を教えて」

### 5. deploy.py
- AWS Lambdaデプロイ自動化スクリプト
- 機能:
  - Poetryからrequirements.txt生成
  - 依存関係の自動インストール
  - ZIPパッケージ作成
  - Lambda関数の作成・更新
  - エラーハンドリング

### 6. env_example.txt
- 環境変数のサンプル設定
- 必要な設定:
  - Google Service Account認証情報
  - スプレッドシートID
  - AWS設定
  - Alexaスキル設定

### 7. README.md
- プロジェクトの完全な設定手順
- 使用方法の説明
- トラブルシューティングガイド
- 開発者向け情報

## 実装のポイント

### 音声インターフェース
- 自然な日本語対話に対応
- エラー時の適切なフィードバック
- ヘルプ機能による使いやすさ向上

### データ管理
- Googleスプレッドシートの自動初期化
- 柔軟な掃除種別設定
- 重要度による優先順位付け

### リマインド機能
- 推奨頻度に基づく自動チェック
- 期限切れ日数の計算
- 重要度順での通知

### コスト最適化
- DynamoDB不使用でコスト削減
- Lambdaの効率的な実行
- 無料のGoogleスプレッドシート活用

## セットアップ開始

### Google Cloud Console サービスアカウント作成手順

#### 1. Google Cloud Consoleにアクセス
1. ブラウザで https://console.cloud.google.com/ にアクセス
2. Googleアカウントでログイン

#### 2. プロジェクトの作成・選択
1. 画面上部のプロジェクト選択ドロップダウンをクリック
2. 「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例: `cleaning-reminder-system`）
4. 「作成」をクリック
5. 作成されたプロジェクトを選択

#### 3. Google Sheets APIの有効化
1. 左サイドバーから「APIとサービス」→「ライブラリ」をクリック
2. 検索ボックスに「Google Sheets API」と入力
3. 「Google Sheets API」を選択
4. 「有効にする」をクリック
5. 同様に「Google Drive API」も有効化（スプレッドシート操作に必要）

#### 4. サービスアカウントの作成
1. 左サイドバーから「APIとサービス」→「認証情報」をクリック
2. 画面上部の「認証情報を作成」→「サービス アカウント」をクリック
3. サービスアカウント情報を入力:
   - **サービス アカウント名**: `cleaning-reminder-service`
   - **サービス アカウントID**: 自動生成（変更可能）
   - **説明**: `掃除記録システム用サービスアカウント`
4. 「作成して続行」をクリック

#### 5. サービスアカウント権限の設定
1. 「このサービス アカウントにプロジェクトへのアクセスを許可する」で:
   - **ロール**: 「編集者」を選択（または最小権限で「Service Account User」）
2. 「続行」をクリック
3. 「ユーザーにこのサービス アカウントへのアクセスを許可」は空白のまま
4. 「完了」をクリック

#### 6. サービスアカウントキーの生成
1. 作成されたサービスアカウントのリストで、先ほど作成したアカウントをクリック
2. 「キー」タブをクリック
3. 「鍵を追加」→「新しい鍵を作成」をクリック
4. **キーのタイプ**: 「JSON」を選択
5. 「作成」をクリック
6. **重要**: JSONファイルが自動ダウンロードされます。このファイルを安全に保存してください

#### 7. 取得した情報
- ✅ サービスアカウントキー（JSONファイル）
- ✅ プロジェクトID（例: `cleaning-reminder-system-12345`）

#### 8. 次のステップ準備
取得したJSONキーファイルの内容を環境変数として設定する準備：
```bash
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account", "project_id": "...", ...}'
```

### JSONキーとは？詳細説明

#### 🔑 JSONキーの正体
**JSONキー**とは、Googleサービスにアクセスするための**デジタル身分証明書**です。

#### 🏠 身近な例で説明
- **家の鍵** → 特定の家にだけ入れる
- **JSONキー** → 特定のGoogleサービスにだけアクセスできる

#### 📄 JSONキーファイルの中身
```json
{
  "type": "service_account",
  "project_id": "cleaning-reminder-system-12345",
  "private_key_id": "a1b2c3d4e5f6...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "cleaning-reminder-service@cleaning-reminder-system-12345.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cleaning-reminder-service%40cleaning-reminder-system-12345.iam.gserviceaccount.com"
}
```

#### 🔍 各項目の説明
- **`type`**: 認証の種類（サービスアカウント）
- **`project_id`**: Google Cloudプロジェクトの識別子
- **`private_key`**: 暗号化された秘密鍵（最重要！）
- **`client_email`**: サービスアカウントのメールアドレス
- **`client_id`**: サービスアカウントの一意ID

#### 💡 なぜJSONキーが必要？
1. **認証**: 「あなたは誰ですか？」→ JSONキーで身元証明
2. **認可**: 「何ができますか？」→ 設定した権限で操作可能
3. **セキュリティ**: パスワードより安全な方式

#### 🔐 JSONキーの使われ方（技術的）
```python
# Pythonコードでの使用例
import gspread
from google.oauth2.service_account import Credentials

# JSONキーから認証情報を作成
credentials = Credentials.from_service_account_info(json_key_data)

# Google Sheets APIにアクセス
gc = gspread.authorize(credentials)

# スプレッドシートを開く
sheet = gc.open_by_key("スプレッドシートID")
```

#### ⚠️ セキュリティの重要性
- **private_key**: これが漏れると他人があなたのGoogleサービスにアクセス可能
- **絶対に秘密**: GitHubなどに公開してはいけない
- **金庫のようなもの**: 安全な場所に保管

#### 🏗️ 我々のシステムでの役割
1. **Lambda関数**がJSONキーを使ってGoogleに「私は掃除記録システムです」と証明
2. **Google**が「OK、スプレッドシートへのアクセスを許可します」と応答
3. **スプレッドシート**に掃除記録を書き込み・読み取りが可能になる

#### 📋 まとめ
- **JSONキー** = Googleサービス用のデジタル身分証明書
- **private_key** = 最も重要な秘密情報
- **目的** = プログラムがGoogleスプレッドシートにアクセスするため
- **保管** = 絶対に秘密にして安全な場所に保存

### Googleスプレッドシート作成・設定手順

#### 1. Googleスプレッドシートの作成
1. ブラウザで https://sheets.google.com/ にアクセス
2. Googleアカウントでログイン
3. 「空白のスプレッドシート」をクリック
4. スプレッドシート名を「掃除記録システム」に変更

#### 2. スプレッドシートIDの取得
1. ブラウザのURLから スプレッドシートIDをコピー
   ```
   https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit
   ```
2. 例: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
3. **重要**: このIDを控えておく（環境変数で使用）

#### 3. サービスアカウントに権限付与
1. スプレッドシートの右上「共有」ボタンをクリック
2. 「ユーザーやグループを追加」欄に以下を入力:
   ```
   cleaning-reminder-service@cleaning-reminder-system-12345.iam.gserviceaccount.com
   ```
   （上記はJSONキーの`client_email`の値）
3. 権限を「編集者」に設定
4. 「送信」をクリック
   - 「メール通知を送信」のチェックは外してOK

#### 4. シート構造の初期設定（手動設定）
我々のシステムは自動でシートを作成しますが、事前に作成する場合：

**シート1: 掃除記録**
| A列（日時） | B列（掃除種別） | C列（実行者） | D列（備考） |
|------------|----------------|--------------|------------|
| 2024-01-15 10:30:00 | トイレ掃除 | ユーザー | Alexa経由 |
| 2024-01-16 14:20:00 | 風呂掃除 | ユーザー | Alexa経由 |

**シート2: 掃除種別設定**
| A列（掃除種別） | B列（推奨頻度（日）） | C列（重要度） | D列（備考） |
|----------------|---------------------|--------------|------------|
| トイレ掃除 | 3 | 高 | 毎日使用 |
| 風呂掃除 | 2 | 高 | カビ防止のため |
| キッチン掃除 | 1 | 高 | 衛生管理 |
| 掃除機 | 7 | 中 | 週1回程度 |
| 床拭き | 7 | 中 | 週1回程度 |
| 窓拭き | 30 | 低 | 月1回程度 |

#### 5. 環境変数の設定
取得したJSONキーとスプレッドシートIDを環境変数として設定：

```bash
# JSONキーファイルの内容をそのまま文字列として設定
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type":"service_account","project_id":"cleaning-reminder-system-12345",...}'

# スプレッドシートID
export GOOGLE_SPREADSHEET_ID="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
```

### GOOGLE_SERVICE_ACCOUNT_KEY 具体的設定方法

#### 📁 ダウンロードしたJSONファイルの場所
Google Cloud Consoleで「鍵を作成」をクリックすると、以下のようなファイル名でダウンロードされます：
```
cleaning-reminder-system-12345-a1b2c3d4e5f6.json
```

#### 🔍 JSONファイルの中身確認
ダウンロードしたJSONファイルをテキストエディタで開くと、以下のような内容になっています：

```json
{
  "type": "service_account",
  "project_id": "cleaning-reminder-system-12345",
  "private_key_id": "a1b2c3d4e5f6g7h8i9j0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDGtJK1XYzR...\n-----END PRIVATE KEY-----\n",
  "client_email": "cleaning-reminder-service@cleaning-reminder-system-12345.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cleaning-reminder-service%40cleaning-reminder-system-12345.iam.gserviceaccount.com"
}
```

#### 💻 環境変数への設定方法

**方法1: macOS/Linux ターミナルで直接設定**
```bash
# JSONファイルの内容を1行の文字列として設定
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type":"service_account","project_id":"cleaning-reminder-system-12345","private_key_id":"a1b2c3d4e5f6g7h8i9j0","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDGtJK1XYzR...\n-----END PRIVATE KEY-----\n","client_email":"cleaning-reminder-service@cleaning-reminder-system-12345.iam.gserviceaccount.com","client_id":"123456789012345678901","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/cleaning-reminder-service%40cleaning-reminder-system-12345.iam.gserviceaccount.com"}'
```

**方法2: ファイルから読み込み**
```bash
# JSONファイルから直接読み込んで設定
export GOOGLE_SERVICE_ACCOUNT_KEY=$(cat ~/Downloads/cleaning-reminder-system-12345-a1b2c3d4e5f6.json)
```

**方法3: .envファイルに保存（推奨）**
プロジェクトディレクトリに`.env`ファイルを作成：
```bash
# .env ファイルの内容
GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account","project_id":"cleaning-reminder-system-12345",...}
GOOGLE_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

#### 🔧 実際の設定例
あなたのJSONファイルをダウンロードしたら、以下のコマンドで設定してください：

```bash
# 1. ダウンロードディレクトリに移動
cd ~/Downloads

# 2. JSONファイル名を確認
ls *.json

# 3. 環境変数に設定（ファイル名は実際のものに置き換え）
export GOOGLE_SERVICE_ACCOUNT_KEY=$(cat cleaning-reminder-system-12345-xxxxxxxxx.json)

# 4. スプレッドシートIDも設定
export GOOGLE_SPREADSHEET_ID="あなたのスプレッドシートID"

# 5. 設定確認
echo $GOOGLE_SERVICE_ACCOUNT_KEY | head -c 50
```

#### ⚠️ 重要な注意点
1. **改行や特殊文字**: JSONの改行文字(`\n`)はそのまま保持
2. **引用符のエスケープ**: JSON内の`"`文字に注意
3. **1行形式**: 環境変数は改行なしの1行文字列として設定
4. **セキュリティ**: .envファイルは.gitignoreに追加して非公開

#### 🧪 設定テスト
設定が正しいかテストする：
```bash
# Poetryで仮想環境を起動
poetry shell

# テスト実行
python -c "
import os
import json
key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
if key:
    data = json.loads(key)
    print(f'Project ID: {data.get(\"project_id\")}')
    print(f'Client Email: {data.get(\"client_email\")}')
    print('JSONキー設定成功！')
else:
    print('JSONキーが設定されていません')
"
```

期待される出力：
```
Project ID: cleaning-reminder-system-12345
Client Email: cleaning-reminder-service@cleaning-reminder-system-12345.iam.gserviceaccount.com
JSONキー設定成功！
```

#### 6. 接続テスト
ローカルでテストを実行して動作確認：
```bash
# Poetryで仮想環境に入る
poetry shell

# テスト実行
python google_sheets_manager.py
```

期待される出力：
```
記録追加結果: True
履歴件数: 1
期限切れ件数: 6  # デフォルト設定の掃除種別数
```

#### 7. 完了確認
- ✅ Googleスプレッドシート作成完了
- ✅ サービスアカウント権限付与完了
- ✅ スプレッドシートID取得完了
- ✅ 環境変数設定完了
- ✅ 接続テスト成功

### 重要な注意事項
⚠️ **セキュリティ**:
- JSONキーファイルは絶対に公開リポジトリにコミットしない
- ローカルファイルとして安全に保管
- 必要に応じてCloud Secret Managerの使用を検討

⚠️ **権限**:
- 最小権限の原則に従い、必要最小限の権限のみ付与
- 定期的なキーローテーションを推奨

⚠️ **スプレッドシート**:
- スプレッドシートIDを正確にコピー
- サービスアカウントのメールアドレスを正確に入力
- 編集権限を付与することを確認

## 次のステップ
1. ✅ Google Cloud Console設定完了
2. ✅ Googleスプレッドシート作成・設定完了
3. ⏳ AWS Lambda関数デプロイ
4. 🔄 Alexaスキル作成・設定
5. ⏳ CloudWatch Eventsスケジュール設定
6. ⏳ 実機テスト・動作確認

## 使用例
```
ユーザー: 「アレクサ、掃除管理を開いて」
Alexa: 「掃除管理システムへようこそ。どの掃除をしましたか？」
ユーザー: 「トイレ掃除をしました」
Alexa: 「トイレ掃除の掃除を記録しました。お疲れ様でした！」
```

```
ユーザー: 「アレクサ、掃除管理を開いて」
Alexa: 「掃除管理システムへようこそ。どの掃除をしましたか？」
ユーザー: 「掃除の状況を教えて」
Alexa: 「以下の掃除が遅れています：風呂掃除が5日、床拭きが10日。時間があるときに掃除してみませんか？」
```

### Alexaスキル作成・設定手順

#### 1. Amazon Developer Consoleにアクセス
1. ブラウザで https://developer.amazon.com/alexa/console/ask にアクセス
2. Amazonアカウントでログイン
   - 既存のAmazonアカウントを使用可能
   - 必要に応じて開発者アカウントに登録

#### 2. 新しいスキルの作成
1. 「スキルの作成」ボタンをクリック
2. スキル基本情報を入力:
   - **スキル名**: `CleaningManagementSkill`
   - **プライマリロケール**: `日本語（日本）`
   - **スキルに追加するモデル**: `カスタム`
   - **スキルをホストする方法**: `ユーザー定義のプロビジョニング`
3. 「スキルを作成」をクリック

#### 3. 呼び出し名の設定
1. 左サイドバーの「呼び出し名」をクリック
2. **スキルの呼び出し名**: `掃除管理` と入力
3. 「モデルを保存」をクリック
