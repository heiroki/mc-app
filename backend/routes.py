from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import cruds
import schemas
from database import get_db

router = APIRouter()


@router.get("/conversations", response_model=list[schemas.ConversationRead])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """ログイン中のユーザーの会話履歴を取得"""
    conversations = cruds.get_conversations(db, user_id=None, skip=skip, limit=limit)
    return [schemas.ConversationRead.from_orm(conv) for conv in conversations]


@router.post("/conversations", response_model=schemas.ConversationRead)
def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
):
    """会話をDBに保存"""
    db_conversation = cruds.create_conversation(db, conversation)
    return schemas.ConversationRead.from_orm(db_conversation)
