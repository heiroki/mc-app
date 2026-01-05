from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.sql import func

from database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    user_input = Column(Text, nullable=False)
    ai_response_words = Column(Text, nullable=True)
    ai_response_advice = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
