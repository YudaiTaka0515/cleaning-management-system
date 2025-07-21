#!/usr/bin/env python3
"""
音声ベース掃除記録システム - デプロイスクリプト

このスクリプトは、Poetryで管理されている依存関係を含めて
AWS Lambdaにデプロイ可能なZIPファイルを作成し、自動的にデプロイします。

使用方法:
    python deploy.py [--no-deploy]

オプション:
    --no-deploy: ZIPファイルの作成のみ行い、デプロイはスキップ

環境変数（必須）:
    - GOOGLE_SERVICE_ACCOUNT_KEY: Google Service Accountのキー（JSON形式）
    - GOOGLE_SPREADSHEET_ID: 対象のGoogle SpreadsheetのID

生成されるファイル:
    - lambda_deployment.zip: AWS Lambdaにアップロード可能なZIPファイル
"""

import argparse
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# 設定
LAMBDA_FUNCTION_NAME = "cleaning-management-alexa-skill"
LAMBDA_RUNTIME = "python3.9"
LAMBDA_HANDLER = "lambda_function.lambda_handler"
LAMBDA_TIMEOUT = 30
LAMBDA_MEMORY_SIZE = 256

EXCLUDE_PATTERNS = [
    "*.pyc",
    "__pycache__",
    "*.git*",
    "*.DS_Store",
    "tests",
    "docs",
    "*.md",
    "pyproject.toml",
    "poetry.lock",
    "deploy.py",
    "archive",
    "*.zip",
]


def log_info(message):
    """情報ログを出力"""
    print(f"ℹ️  {message}")


def log_success(message):
    """成功ログを出力"""
    print(f"✅ {message}")


def log_error(message):
    """エラーログを出力"""
    print(f"❌ {message}")


def log_warning(message):
    """警告ログを出力"""
    print(f"⚠️  {message}")


def check_aws_credentials(profile=None):
    """AWS認証情報をチェック"""
    try:
        session = boto3.Session(profile_name=profile)
        credentials = session.get_credentials()
        if credentials is None:
            return False

        # 実際にAWSサービスにアクセスして認証をテスト
        sts = session.client("sts")
        caller_identity = sts.get_caller_identity()
        log_info(f"🔐 AWS認証成功 - アカウント: {caller_identity.get('Account', 'Unknown')}")
        if profile:
            log_info(f"📋 使用プロファイル: {profile}")
        return True
    except (NoCredentialsError, ClientError) as e:
        log_error(f"AWS認証エラー: {e}")
        return False


def check_environment_variables():
    """必要な環境変数をチェック"""
    required_vars = ["GOOGLE_SERVICE_ACCOUNT_KEY", "GOOGLE_SPREADSHEET_ID"]
    missing_vars = []

    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    return missing_vars


def create_deployment_package():
    """デプロイメントパッケージを作成"""

    log_info("🚀 デプロイメントパッケージ作成開始")

    # 現在のディレクトリを取得
    project_root = Path.cwd()

    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        package_dir = temp_path / "package"
        package_dir.mkdir()

        log_info("📦 依存関係をインストール中...")

        # Poetry環境から依存関係をコピー
        try:
            # Poetry仮想環境のパスを取得
            result = subprocess.run(["poetry", "env", "info", "--path"], capture_output=True, text=True, check=True)
            venv_path = Path(result.stdout.strip())
            site_packages = venv_path / "lib" / "python3.9" / "site-packages"

            if not site_packages.exists():
                # Python 3.10以上の場合
                site_packages_dirs = list(venv_path.glob("lib/python*/site-packages"))
                if site_packages_dirs:
                    site_packages = site_packages_dirs[0]
                else:
                    raise FileNotFoundError("site-packages directory not found")

            log_info(f"📚 依存関係をコピー中: {site_packages}")

            # 必要なパッケージのみをコピー
            required_packages = [
                "ask_sdk_core",
                "ask_sdk_model",
                "ask_sdk_runtime",
                "gspread",
                "google",
                "google_auth",
                "google_auth_oauthlib",
                "oauthlib",
                "requests_oauthlib",
                "requests",
                "urllib3",
                "certifi",
                "charset_normalizer",
                "idna",
                "pyasn1",
                "pyasn1_modules",
                "rsa",
                "cachetools",
                "six",
                "dateutil",
                "yaml",
                "pyyaml",
            ]

            copied_packages = []
            for item in site_packages.iterdir():
                if item.is_dir():
                    package_name = item.name.replace("-", "_").lower()
                    base_name = package_name.split(".")[0]

                    if any(req in package_name or req in base_name for req in required_packages):
                        shutil.copytree(item, package_dir / item.name)
                        copied_packages.append(item.name)
                elif item.suffix == ".dist-info":
                    package_name = item.name.replace("-", "_").lower()
                    base_name = package_name.split(".")[0]

                    if any(req in package_name or req in base_name for req in required_packages):
                        shutil.copytree(item, package_dir / item.name)

            log_success(f"📦 {len(copied_packages)}個のパッケージをコピーしました")

        except subprocess.CalledProcessError as e:
            log_error(f"Poetry環境の取得に失敗: {e}")
            return False
        except Exception as e:
            log_error(f"依存関係のコピーに失敗: {e}")
            return False

        # プロジェクトファイルをコピー
        log_info("📄 プロジェクトファイルをコピー中...")

        # メインファイル
        shutil.copy2(project_root / "lambda_function.py", package_dir / "lambda_function.py")

        # srcディレクトリ
        if (project_root / "src").exists():
            shutil.copytree(project_root / "src", package_dir / "src")

        # configディレクトリ（YAMLファイル用）
        if (project_root / "config").exists():
            shutil.copytree(project_root / "config", package_dir / "config")

        # 最終的なlambda_function_final.pyがあれば、それをバックアップとして含める
        if (project_root / "lambda_function_final.py").exists():
            shutil.copy2(project_root / "lambda_function_final.py", package_dir / "lambda_function_final.py")

        log_success("📄 プロジェクトファイルのコピー完了")

        # ZIPファイルを作成
        zip_path = project_root / "lambda_deployment.zip"
        if zip_path.exists():
            zip_path.unlink()

        log_info("🗜️  ZIPファイルを作成中...")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(package_dir)
                    zipf.write(file_path, arc_path)

                    # YAMLファイルの場合は詳細をログ出力
                    if file.endswith(".yaml") or file.endswith(".yml"):
                        log_info(f"📄 YAMLファイルを追加: {arc_path} (元: {file_path})")

                        # ファイル内容の最初の数行を確認
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                first_lines = [f.readline().strip() for _ in range(3)]
                                log_info(f"   内容確認: {first_lines}")
                        except Exception as e:
                            log_warning(f"   ファイル内容確認エラー: {e}")

        # zipファイル内の構造を確認
        log_info("📋 作成されたZIPファイルの構造確認:")
        with zipfile.ZipFile(zip_path, "r") as zipf:
            file_list = zipf.namelist()
            config_files = [f for f in file_list if "config" in f or f.endswith(".yaml")]
            if config_files:
                log_info("🔧 設定ファイル:")
                for cf in config_files:
                    log_info(f"   • {cf}")
            else:
                log_warning("⚠️  設定ファイルがZIPに含まれていません！")

        # ファイルサイズを確認
        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)

        log_success("🎉 デプロイメントパッケージ作成完了!")
        log_info(f"📊 ファイル: {zip_path}")
        log_info(f"📊 サイズ: {zip_size_mb:.2f} MB")

        if zip_size_mb > 50:
            log_warning("⚠️  ファイルサイズが50MBを超えています。AWS Lambdaの制限を確認してください。")

        return True


def deploy_to_lambda(zip_path, profile=None):
    """AWS Lambdaに自動デプロイ"""
    log_info("🚀 AWS Lambdaへのデプロイ開始")

    try:
        session = boto3.Session(profile_name=profile)
        lambda_client = session.client("lambda")

        # Lambda関数が存在するかチェック
        try:
            response = lambda_client.get_function(FunctionName=LAMBDA_FUNCTION_NAME)
            function_exists = True
            log_info(f"✨ 既存のLambda関数を発見: {LAMBDA_FUNCTION_NAME}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                function_exists = False
                log_info(f"🆕 新規Lambda関数を作成します: {LAMBDA_FUNCTION_NAME}")
            else:
                raise

        # ZIPファイルを読み込み
        with open(zip_path, "rb") as zip_file:
            zip_content = zip_file.read()

        if function_exists:
            # 既存関数のコードを更新
            log_info("📤 Lambda関数のコードを更新中...")
            response = lambda_client.update_function_code(FunctionName=LAMBDA_FUNCTION_NAME, ZipFile=zip_content)
            log_success("✅ Lambda関数のコード更新完了")

            # コード更新完了を待機
            log_info("⏳ コード更新完了を待機中...")
            waiter = lambda_client.get_waiter("function_updated")
            waiter.wait(FunctionName=LAMBDA_FUNCTION_NAME)
            log_success("✅ コード更新待機完了")

            # 関数設定を更新（リトライ付き）
            log_info("⚙️  Lambda関数の設定を更新中...")
            max_retries = 3
            retry_delay = 10  # 秒

            for attempt in range(max_retries):
                try:
                    lambda_client.update_function_configuration(
                        FunctionName=LAMBDA_FUNCTION_NAME,
                        Runtime=LAMBDA_RUNTIME,
                        Handler=LAMBDA_HANDLER,
                        Timeout=LAMBDA_TIMEOUT,
                        MemorySize=LAMBDA_MEMORY_SIZE,
                    )
                    log_success("✅ Lambda関数の設定更新完了")
                    break
                except ClientError as e:
                    if "ResourceConflictException" in str(e) and attempt < max_retries - 1:
                        log_warning(f"⚠️  設定更新で競合エラー（試行 {attempt + 1}/{max_retries}）")
                        log_info(f"⏳ {retry_delay}秒待機してリトライします...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise

        else:
            # 新規関数を作成する場合は、IAMロールの取得が必要
            log_warning("⚠️  新規Lambda関数の作成にはIAMロールが必要です")
            log_info("💡 以下の方法でIAMロールを作成してください:")
            print("   1. AWS IAMコンソールでLambda実行ロールを作成")
            print("   2. AWSLambdaBasicExecutionRole ポリシーをアタッチ")
            print("   3. 作成されたロールのARNをコピー")

            # 簡易的なロール名を推測（実際の環境では適切に設定）
            sts_client = session.client("sts")
            account_id = sts_client.get_caller_identity()["Account"]
            role_name = "lambda-execution-role"  # 一般的なロール名
            role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

            log_info(f"🔧 推測されるロールARN: {role_arn}")
            log_info("📝 このロールが存在しない場合、IAMコンソールで作成してください")

            # 新規関数を作成
            log_info("🆕 新しいLambda関数を作成中...")
            try:
                response = lambda_client.create_function(
                    FunctionName=LAMBDA_FUNCTION_NAME,
                    Runtime=LAMBDA_RUNTIME,
                    Role=role_arn,
                    Handler=LAMBDA_HANDLER,
                    Code={"ZipFile": zip_content},
                    Timeout=LAMBDA_TIMEOUT,
                    MemorySize=LAMBDA_MEMORY_SIZE,
                    Description="音声ベース掃除記録システム - Alexa Skill",
                )
                log_success("✅ 新しいLambda関数の作成完了")
            except ClientError as e:
                if "role" in str(e).lower():
                    log_error(f"IAMロールエラー: {e}")
                    log_info("💡 以下のコマンドでロールを作成できます:")
                    profile_name = profile or "default"
                    print(
                        f"   aws iam create-role --role-name lambda-execution-role "
                        f"--assume-role-policy-document file://trust-policy.json "
                        f"--profile {profile_name}"
                    )
                    return False
                else:
                    raise

        # 環境変数を設定
        log_info("🔧 環境変数を設定中...")
        environment_variables = {
            "GOOGLE_SERVICE_ACCOUNT_KEY": os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY"),
            "GOOGLE_SPREADSHEET_ID": os.environ.get("GOOGLE_SPREADSHEET_ID"),
        }

        # 環境変数更新（リトライ付き）
        max_retries = 3
        retry_delay = 10  # 秒

        for attempt in range(max_retries):
            try:
                lambda_client.update_function_configuration(
                    FunctionName=LAMBDA_FUNCTION_NAME, Environment={"Variables": environment_variables}
                )
                log_success("✅ 環境変数の設定完了")
                break
            except ClientError as e:
                if "ResourceConflictException" in str(e) and attempt < max_retries - 1:
                    log_warning(f"⚠️  環境変数更新で競合エラー（試行 {attempt + 1}/{max_retries}）")
                    log_info(f"⏳ {retry_delay}秒待機してリトライします...")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise

        # デプロイ完了を待機
        log_info("⏳ デプロイ完了を待機中...")
        waiter = lambda_client.get_waiter("function_updated")
        waiter.wait(FunctionName=LAMBDA_FUNCTION_NAME)

        # 最終確認
        response = lambda_client.get_function(FunctionName=LAMBDA_FUNCTION_NAME)
        function_arn = response["Configuration"]["FunctionArn"]

        log_success("🎉 AWS Lambdaへのデプロイ完了!")
        log_info(f"📋 関数ARN: {function_arn}")
        log_info(f"📋 ランタイム: {response['Configuration']['Runtime']}")
        log_info(f"📋 ハンドラー: {response['Configuration']['Handler']}")
        log_info(f"📋 メモリ: {response['Configuration']['MemorySize']}MB")
        log_info(f"📋 タイムアウト: {response['Configuration']['Timeout']}秒")

        return True

    except ClientError as e:
        log_error(f"AWS Lambda操作エラー: {e}")
        return False
    except Exception as e:
        log_error(f"予期しないエラー: {e}")
        return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="音声ベース掃除記録システム - デプロイスクリプト")
    parser.add_argument("--no-deploy", action="store_true", help="ZIPファイルの作成のみ行い、デプロイはスキップ")
    parser.add_argument("--profile", help="使用するAWSプロファイル名（デフォルト: indivisual）", default="indivisual")
    args = parser.parse_args()

    print("🧹 音声ベース掃除記録システム - デプロイスクリプト")
    print("=" * 60)

    # Poetryがインストールされているか確認
    try:
        subprocess.run(["poetry", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("Poetryがインストールされていません。先にPoetryをインストールしてください。")
        return 1

    # 依存関係がインストールされているか確認
    try:
        subprocess.run(
            ["poetry", "run", "python", "-c", "import ask_sdk_core, gspread, yaml"], capture_output=True, check=True
        )
    except subprocess.CalledProcessError:
        log_warning("依存関係がインストールされていません。インストール中...")
        try:
            subprocess.run(["poetry", "install"], check=True)
            log_success("依存関係のインストール完了")
        except subprocess.CalledProcessError as e:
            log_error(f"依存関係のインストールに失敗: {e}")
            return 1

    # デプロイメントパッケージを作成
    if not create_deployment_package():
        log_error("デプロイメントパッケージの作成に失敗しました")
        return 1

    # デプロイスキップの場合
    if args.no_deploy:
        log_info("🔄 --no-deployオプションが指定されているため、デプロイをスキップします")
        print("\n🎯 手動デプロイの手順:")
        print("1. AWS Lambdaコンソールにアクセス")
        print(f"2. 関数「{LAMBDA_FUNCTION_NAME}」を選択")
        print("3. 「lambda_deployment.zip」をアップロード")
        print("4. 環境変数を設定:")
        print("   - GOOGLE_SERVICE_ACCOUNT_KEY")
        print("   - GOOGLE_SPREADSHEET_ID")
        print("5. Alexaスキルのエンドポイントを確認")
        return 0

    # 環境変数をチェック
    missing_vars = check_environment_variables()
    if missing_vars:
        log_error("以下の環境変数が設定されていません:")
        for var in missing_vars:
            print(f"   - {var}")
        log_info("環境変数を設定してから再実行してください")
        return 1

    # AWS認証情報をチェック
    if not check_aws_credentials(args.profile):
        log_error("AWS認証情報が設定されていません")
        log_info("以下のいずれかの方法でAWS認証を설정してください:")
        print(f"1. AWS CLI: aws configure --profile {args.profile}")
        print("2. 環境変数: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("3. IAMロール（EC2インスタンス等）")
        log_info(f"📋 指定プロファイル: {args.profile}")
        return 1

    # AWS Lambdaに自動デプロイ
    zip_path = Path.cwd() / "lambda_deployment.zip"
    if deploy_to_lambda(zip_path, args.profile):
        print("\n🎯 次のステップ:")
        print("1. Alexa Developer Consoleにアクセス")
        print("2. スキルのエンドポイントにLambda関数のARNを設定")
        print("3. スキルをテスト")
        return 0
    else:
        log_error("AWS Lambdaへのデプロイに失敗しました")
        return 1


if __name__ == "__main__":
    exit(main())
