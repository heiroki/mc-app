import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# =============================
# AI生成用スキーマ
# =============================
class InputData(BaseModel):
    text: str = Field(min_length=1, max_length=140, description="入力文")


class OutputData(BaseModel):
    minus_words: list[str] = Field(..., description="検出されたマイナスワード")
    advice: str = Field(..., description="アドバイス文")


# =============================
# 会話履歴用スキーマ
# =============================
class ConversationCreate(BaseModel):
    user_id: int | None = None
    user_input: str = Field(..., min_length=1, max_length=500)
    ai_response_words: list[str] = Field(..., description="検出されたマイナスワード")
    ai_response_advice: str = Field(..., min_length=1, description="アドバイス文")


class ConversationRead(BaseModel):
    id: int
    user_id: int | None
    user_input: str
    ai_response_words: list[str] | None
    ai_response_advice: str | None
    created_at: datetime

    @classmethod
    def from_orm(cls, obj: Any):
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            user_input=obj.user_input,
            ai_response_words=json.loads(obj.ai_response_words) if obj.ai_response_words else [],
            ai_response_advice=obj.ai_response_advice,
            created_at=obj.created_at,
        )

    class Config:
        from_attributes = True
