from datetime import datetime
 
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
 
from backend.database import Base
 
 
class Conversation(Base):

    tablename = "conversations"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    user_one_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user_two_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
 
 
class Message(Base):
    tablename = "messages"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)