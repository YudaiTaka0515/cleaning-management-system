# 🧹 掃除管理システム可視化ダッシュボード

Alexaスキルで記録した掃除データを可視化するStreamlitアプリケーションです。

## ✨ 主な機能

- 📅 **Contribution Calendar**: GitHubのような掃除実施履歴の可視化
- ⚠️ **期限切れ状況**: 期限切れの掃除をリアルタイムで確認
- 🔄 **掃除サイクル分析**: 各掃除種別の実施間隔を分析
- 📊 **統計ダッシュボード**: 掃除実施回数や頻度の統計
- 🍅 **ポモドーロタイマー**: 掃除作業時の集中支援

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
# Poetryを使用
cd visualizer
poetry install

# または pip を使用
pip install -r requirements.txt
```

### 2. 環境変数の設定

以下の環境変数を設定してください：

```bash
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
export GOOGLE_SPREADSHEET_ID='your-spreadsheet-id'
```

### 3. アプリケーションの起動

```bash
# Poetryを使用
poetry run streamlit run main.py

# または
streamlit run main.py
```

## 📋 使用方法

### ダッシュボード
- 掃除の概要統計を確認
- 期限切れの掃除を確認
- 最近の掃除記録を確認

### ポモドーロタイマー
- 作業時間: 25分
- 短い休憩: 5分
- 長い休憩: 15分（4ポモドーロ後）

### 詳細分析
- Contribution Calendar形式での履歴表示
- 掃除サイクルの分析
- 期間別の頻度分析

## 🔧 設定

### 掃除種別設定
- トイレ掃除（3日周期、高優先度）
- 風呂掃除（7日周期、高優先度）
- キッチン掃除（3日周期、高優先度）
- 床掃除（7日周期、中優先度）
- 窓掃除（14日周期、低優先度）
- 掃除機かけ（3日周期、中優先度）

### ポモドーロ設定
- 作業時間: 25分
- 短い休憩: 5分
- 長い休憩: 15分
- 長い休憩の間隔: 4ポモドーロ

## 📊 データ構造

### 掃除記録シート
| 列 | 内容 |
|----|------|
| A | 日時 |
| B | 掃除種別 |
| C | 記録者 |
| D | 備考 |

### 掃除種別設定シート
| 列 | 内容 |
|----|------|
| A | 掃除種別 |
| B | 推奨頻度（日） |
| C | 最終実施日 |
| D | 次回予定日 |
| E | 優先度 |

## 🛠️ 開発

### プロジェクト構造

```
visualizer/
├── cleaning_visualizer/
│   ├── __init__.py
│   ├── app.py              # メインアプリケーション
│   ├── config.py           # 設定管理
│   ├── data_manager.py     # データ管理
│   ├── visualization.py    # 可視化コンポーネント
│   └── pomodoro.py         # ポモドーロタイマー
├── main.py                 # エントリーポイント
├── pyproject.toml          # Poetry設定
└── README.md               # このファイル
```

### コード整形

```bash
poetry run black cleaning_visualizer/
poetry run flake8 cleaning_visualizer/
```

### テスト

```bash
poetry run pytest
```

## 🔗 関連プロジェクト

- [Alexa Skill](../alexa-skill/): 音声による掃除記録システム

## 📞 サポート

何か問題があれば、GitHubのIssuesに報告してください。

## �� ライセンス

MIT License 