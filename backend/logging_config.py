# backend/logging_config.py（新規・完全版）

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
from config import APP_DATA_DIR, APP_VERSION, APP_NAME

def setup_logging(log_level=logging.INFO):
    """
    ログ設定（ファイル + コンソール）
    
    Args:
        log_level: ログレベル（デフォルト: INFO）
    """
    
    # ログディレクトリ
    log_dir = APP_DATA_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'backend.log'
    
    # ログフォーマット
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ファイルハンドラ（10MB×5ファイルでローテーション）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # ファイルには詳細ログ
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)  # コンソールは指定レベル
    
    # ルートロガー設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 最も詳細なレベル
    
    # 既存のハンドラをクリア（重複防止）
    root_logger.handlers.clear()
    
    # 新しいハンドラを追加
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # uvicornのログレベルも調整
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # アクセスログは警告以上
    
    # 起動時情報
    logging.info("=" * 60)
    logging.info(f"🚀 {APP_NAME} v{APP_VERSION}")
    logging.info(f"📝 ログシステム初期化完了")
    logging.info(f"Python: {sys.version}")
    logging.info(f"実行ファイル: {sys.executable}")
    logging.info(f"ログファイル: {log_file}")
    logging.info("=" * 60)

# モジュールインポート時に自動実行
setup_logging()
