# backend/ai_routes.py（修正版）

from fastapi import APIRouter, HTTPException
import logging

from ai_model import generate_advice
from schemas import InputData, OutputData

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate", response_model=OutputData)
async def generate_text(payload: InputData):
    """マイナスワード検出エンドポイント"""
    input_text = (payload.text or "").strip()
    
    if not input_text:
        logger.warning("⚠️ 空の入力が送信されました")
        raise HTTPException(status_code=400, detail="入力が空です")

    logger.info(f"マイナスワード検出リクエスト: {input_text[:50]}...")

    try:
        # マイナスワード検出（asyncに変更）
        result = await generate_advice(input_text)

        logger.info(f"✅ マイナスワード検出完了: {len(result['minus_words'])}個")

        return OutputData(
            minus_words=result["minus_words"],
            advice=result["advice"]
        )
    
    except Exception as e:
        logger.error(f"❌ マイナスワード検出エラー: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI生成に失敗: {str(e)}"
        ) from e
    