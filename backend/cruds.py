import json

from sqlalchemy.orm import Session

from models import Conversation
from schemas import ConversationCreate


# =============================
# 会話履歴関連
# =============================
def create_conversation(db: Session, conversation: ConversationCreate):
    """会話を保存（listをJSON文字列に変換）"""
    db_conversation = Conversation(
        user_id=conversation.user_id,
        user_input=conversation.user_input,
        ai_response_words=json.dumps(conversation.ai_response_words, ensure_ascii=False),
        ai_response_advice=conversation.ai_response_advice
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_conversations(db: Session, user_id: int | None = None, skip: int = 0, limit: int = 100):
    """会話履歴を取得"""
    query = db.query(Conversation)
    if user_id is not None:
        query = query.filter(Conversation.user_id == user_id)
    return query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()
