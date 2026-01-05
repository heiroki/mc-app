# backend/database.py（修正版）

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

logger.info(f"📊 データベース接続: {DATABASE_URL}")

# SQLite用のエンジン作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite用（マルチスレッド対応）
    echo=False  # 本番環境ではFalse推奨
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()

def init_db():
    """データベースを初期化（テーブル作成）"""
    logger.info("🔄 データベース初期化中...")
    try:
        # models.pyのクラス定義からテーブルを自動作成
        from models import Conversation  # noqa: F401
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ データベース初期化完了")
    except Exception as e:
        logger.error(f"❌ データベース初期化エラー: {e}")
        raise

def get_db():
    """FastAPIのDependsで使えるセッション取得関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
