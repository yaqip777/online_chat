from datetime import datetime, timedelta
 
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
 
from backend.database import Base
 
 
def _default_expiry() -> datetime:
    return datetime.utcnow() + timedelta(hours=24)
 
 
class Story(Base):
 
    __tablename__ = "stories"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    video_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=_default_expiry)
 