# # ========================================
# # 修正: wc_routes.py（SQLAlchemy 2.0対応）
# # 変更点: session.execute() + scalars()を使用
# # ========================================
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Conversation
from wc_model import WordCloudGenerator

router = APIRouter()

generator = WordCloudGenerator()


@router.post("/wordcloud/generate")
async def generate_wordcloud(
    user_id: int | None = Query(None, description="ユーザーID（指定しない場合は全ユーザー）"),
    limit: int | None = Query(None, description="取得件数の上限"),
    width: int = Query(800, ge=400, le=2000, description="画像幅"),
    height: int = Query(400, ge=200, le=1000, description="画像高さ"),
    colormap: str = Query('Reds', description="カラーマップ"),
    db: Session = Depends(get_db)
):
    """minus_wordsからワードクラウド画像を生成"""

    try:
        # クエリ構築
        stmt = select(Conversation.ai_response_words).filter(
            Conversation.ai_response_words.isnot(None)
        )

        # user_idが指定されていれば絞り込み
        if user_id is not None:
            stmt = stmt.filter(Conversation.user_id == user_id)

        stmt = stmt.order_by(Conversation.created_at.desc())

        # 件数制限
        if limit is not None and limit > 0:
            stmt = stmt.limit(limit)

        results = db.execute(stmt).scalars().all()

        # JSON配列をパース
        all_minus_words = []
        for value in results:
            if value:
                try:
                    words_list = json.loads(value)
                    if isinstance(words_list, list):
                        all_minus_words.extend(words_list)
                except json.JSONDecodeError as e:
                    print(f"[WARNING] JSON decode error: {e}, value: {value}")
                    continue

        print(f"[DEBUG] All minus words: {all_minus_words}")

        if not all_minus_words:
            raise HTTPException(status_code=404, detail="マイナスワードが見つかりません")

        # ワードクラウド画像生成
        img_io = generator.generate_wordcloud_image(
            words=all_minus_words,
            width=width,
            height=height,
            colormap=colormap
        )

        return StreamingResponse(
            img_io,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=wordcloud_minus_words.png",
                "Cache-Control": "no-cache"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Wordcloud generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"ワードクラウド生成エラー: {e}") from e


@router.get("/wordcloud/test")
async def test_wordcloud():
    """テスト用エンドポイント"""
    test_words = ["ダメ", "無理", "できない", "辛い", "疲れた", "嫌だ"]

    img_io = generator.generate_wordcloud_image(
        words=test_words,
        width=800,
        height=400,
        colormap='Reds'
    )

    return StreamingResponse(img_io, media_type="image/png")
