# backend/main.py（修正版）

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

# ログ設定を最初にインポート
from logging_config import setup_logging

# その他のインポート
from config import APP_VERSION, APP_NAME
from database import init_db
from inference_manager import get_inference_manager

# ルーターのインポート
import routes
import ai_routes
import wc_routes

logger = logging.getLogger(__name__)

# FastAPIアプリケーション作成
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Desktop AI Application with Local LLM"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(ai_routes.router)
app.include_router(routes.router)
app.include_router(wc_routes.router)

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("=" * 60)
    logger.info("🚀 アプリケーション起動中...")
    logger.info("=" * 60)
    
    # データベース初期化
    try:
        init_db()
    except Exception as e:
        logger.error(f"❌ データベース初期化失敗: {e}")
        sys.exit(1)
    
    # 推論エンジン初期化
    try:
        inference_manager = get_inference_manager()
        logger.info("✅ 推論エンジン初期化完了")
    except Exception as e:
        logger.error(f"❌ 推論エンジン初期化失敗: {e}")
        sys.exit(1)
    
    logger.info("✅ アプリケーション起動完了")

@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーションシャットダウン時の処理"""
    logger.info("🛑 アプリケーションシャットダウン中...")
    
    from inference_manager import inference_manager
    if inference_manager:
        inference_manager.shutdown()
    
    logger.info("✅ シャットダウン完了")

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    from inference_manager import inference_manager
    
    return {
        "status": "ok",
        "version": APP_VERSION,
        "model_loaded": inference_manager is not None and inference_manager.llm is not None
    }

if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    
    uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")
