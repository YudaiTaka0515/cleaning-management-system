# 🚀 掃除管理ダッシュボード - デプロイガイド

## 📋 Streamlit Cloud デプロイ手順

### 前提条件
- GitHubアカウント
- Google Cloud Serviceアカウント
- Google Sheets（掃除記録用）

---

## Step 1: GitHubリポジトリの作成

1. GitHubで新しいリポジトリを作成
2. ローカルプロジェクトをGitHubにプッシュ

```bash
# Git初期化（まだの場合）
git init
git add .
git commit -m "Initial commit: 掃除管理ダッシュボード"

# GitHubリポジトリを追加してプッシュ
git remote add origin https://github.com/your-username/cleaning-management-system.git
git branch -M main
git push -u origin main
```

---

## Step 2: Streamlit Cloud アプリ作成

1. [Streamlit Cloud](https://share.streamlit.io/) にアクセス
2. GitHubアカウントでログイン
3. 「New app」をクリック
4. 以下の設定でアプリを作成：
   - **Repository**: `your-username/cleaning-management-system`
   - **Branch**: `main`
   - **Main file path**: `visualizer/main.py`
   - **App URL**: 任意のURLを設定（例：`cleaning-dashboard`）

---

## Step 3: Secrets設定

Streamlit CloudのSecretsでGoogle Sheetsの認証情報を設定：

1. デプロイしたアプリの管理画面に移動
2. 「Settings」→「Secrets」を開く
3. 以下の形式でSecretsを追加：

```toml
[google]
service_account_key = '''
{
  "type": "service_account",
  "project_id": "your-actual-project-id",
  "private_key_id": "your-actual-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_ACTUAL_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-actual-service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-actual-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
}
'''
spreadsheet_id = "your-actual-spreadsheet-id"
```

⚠️ **重要**: 
- `your-actual-*` の部分を実際の値に置き換えてください
- private_keyの改行文字 `\n` は必須です
- JSONの外側に `'''` を付けてください

---

## Step 4: Google Sheets権限設定

1. Google Cloud Consoleでサービスアカウントのメールアドレスを確認
2. Google Sheetsで以下のシートを作成：
   - **掃除記録**: 列A=日時, B=掃除種別, C=記録者, D=備考
   - **掃除種別設定**: 列A=掃除種別, B=推奨頻度（日）, C=最終実施日, D=次回予定日, E=優先度
3. サービスアカウントに編集権限を付与

---

## Step 5: デプロイ確認

1. アプリが正常にデプロイされることを確認
2. Google Sheetsからデータが取得できることを確認
3. 各機能が動作することをテスト：
   - 📊 ダッシュボード
   - 🍅 ポモドーロタイマー
   - 📈 詳細分析
   - ⚙️ 設定

---

## 🔧 トラブルシューティング

### よくある問題

#### 1. Google Sheets接続エラー
```
GOOGLE_SERVICE_ACCOUNT_KEY環境変数またはStreamlit Secretsが設定されていません
```

**解決方法**:
- Streamlit CloudのSecretsが正しく設定されているか確認
- JSONのフォーマットが正しいか確認
- private_keyの改行文字が正しく設定されているか確認

#### 2. スプレッドシートアクセスエラー
```
Google Sheets初期化エラー: [403] The caller does not have permission
```

**解決方法**:
- サービスアカウントにスプレッドシートの編集権限を付与
- スプレッドシートIDが正しいか確認

#### 3. モジュール読み込みエラー
```
ModuleNotFoundError: No module named 'cleaning_visualizer'
```

**解決方法**:
- Main file pathが `visualizer/main.py` に設定されているか確認
- requirements.txtがvisualizerディレクトリに存在するか確認

---

## 🔄 アップデート方法

1. ローカルで変更をコミット
```bash
git add .
git commit -m "Update: 新機能追加"
git push
```

2. Streamlit Cloudが自動的にデプロイ
3. アプリが正常に動作することを確認

---

## 📱 カスタムドメイン設定

Streamlit Cloudの有料プランでは、カスタムドメインの設定が可能です：

1. アプリ設定の「Custom domain」を開く
2. 独自ドメインを設定
3. DNS設定を行う

---

## 🔒 セキュリティ考慮事項

1. **機密情報の管理**:
   - GitHubリポジトリに機密情報をコミットしない
   - Streamlit Cloud Secretsを活用する

2. **アクセス制御**:
   - 必要に応じてBasic認証を追加
   - IPアドレス制限の検討

3. **データ保護**:
   - Google Sheets権限の最小化
   - 定期的なアクセスログの確認

---

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. Streamlit Cloud のログ
2. Google Cloud Console のAPI使用量
3. Google Sheets の権限設定

デプロイに関する詳細情報は、[Streamlit公式ドキュメント](https://docs.streamlit.io/streamlit-cloud) を参照してください。 