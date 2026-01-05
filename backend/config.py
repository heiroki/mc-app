# backend/config.py（新規・完全版）

import os
import sys
from pathlib import Path

# アプリケーション情報
APP_VERSION = "1.0.0"
APP_NAME = "MyOllamaApp"

# APIサーバー設定
API_HOST = "127.0.0.1"
API_PORT = 8000

def get_base_dir():
    """
    実行ファイルのベースディレクトリを取得
    
    Returns:
        Path: ベースディレクトリのパス
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでexe化されている場合
        return Path(sys.executable).parent
    else:
        # 開発環境（.pyファイルから実行）
        return Path(__file__).parent

def get_app_data_dir():
    """
    アプリケーションデータディレクトリを取得
    
    Returns:
        Path: アプリケーションデータディレクトリのパス
    """
    if sys.platform == 'win32':
        # Windows: %LOCALAPPDATA%\MyOllamaApp
        app_data = Path(os.environ.get('LOCALAPPDATA', ''))
        if not app_data:
            # フォールバック
            app_data = Path.home() / 'AppData' / 'Local'
    else:
        # その他のOS（念のため）
        app_data = Path.home() / '.local' / 'share'
    
    app_dir = app_data / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir

def get_model_path():
    """
    モデルファイルのパスを取得（優先順位付き）
    
    Returns:
        str: モデルファイルのパス
    
    Raises:
        FileNotFoundError: モデルファイルが見つからない場合
    """
    base_dir = get_base_dir()
    app_data_dir = get_app_data_dir()
    
    # モデルファイル名
    model_name = "gemma-2-2b-jpn-it-Q4_K_M.gguf"
    
    # 優先順位1: %LOCALAPPDATA%\MyOllamaApp\models
    localappdata_model = app_data_dir / 'models' / model_name
    
    # 優先順位2: 実行ファイルと同じ場所の models/
    local_model = base_dir / 'models' / model_name
    
    # 優先順位3: 一つ上の models/（開発環境用）
    dev_model = base_dir.parent / 'models' / model_name
    
    # 優先順位4: カレントディレクトリの models/
    current_model = Path.cwd() / 'models' / model_name
    
    # 順番に確認
    for model_path in [localappdata_model, local_model, dev_model, current_model]:
        if model_path.exists():
            print(f"✅ モデル検出: {model_path}")
            return str(model_path)
    
    # 見つからない場合
    error_msg = f"""
    ❌ モデルファイルが見つかりません: {model_name}
    
    確認場所：
    1. {localappdata_model}
    2. {local_model}
    3. {dev_model}
    4. {current_model}
    
    モデルファイルを以下からダウンロードして配置してください：
    https://huggingface.co/mmnga/gemma-2-2b-jpn-it-gguf
    """
    raise FileNotFoundError(error_msg)

def get_database_url():
    """
    データベースURLを取得
    
    Returns:
        str: SQLiteデータベースのURL
    """
    app_data_dir = get_app_data_dir()
    db_dir = app_data_dir / 'data'
    db_dir.mkdir(exist_ok=True)
    
    db_path = db_dir / 'app.db'
    
    # SQLiteのURL形式（Windowsパス対応）
    # file:///C:/Users/.../app.db の形式
    return f"sqlite:///{str(db_path).replace(os.sep, '/')}"

# 設定値をエクスポート
BASE_DIR = get_base_dir()
APP_DATA_DIR = get_app_data_dir()

# モデルパスは起動時エラーを防ぐため、関数として公開
# MODEL_PATH = get_model_path()  ← これだとインポート時にエラーになる可能性
try:
    MODEL_PATH = get_model_path()
except FileNotFoundError as e:
    # モデルが見つからない場合は警告のみ（起動時に再度チェック）
    MODEL_PATH = None
    print(f"⚠️ 警告: {e}")

DATABASE_URL = get_database_url()

# 起動時に設定情報を表示
print("=" * 60)
print(f"📦 {APP_NAME} v{APP_VERSION}")
print("=" * 60)
print(f"📁 ベースディレクトリ: {BASE_DIR}")
print(f"📁 アプリデータ: {APP_DATA_DIR}")
print(f"🤖 モデルパス: {MODEL_PATH if MODEL_PATH else '未設定'}")
print(f"💾 データベース: {DATABASE_URL}")
print(f"🌐 APIサーバー: http://{API_HOST}:{API_PORT}")
print("=" * 60)
