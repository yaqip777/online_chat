from datetime import datetime

from pydantic import BaseModel


class StoryResponseSchema(BaseModel):
    id: int
    user_id: int
    image_url: str | None
    video_url: str | None
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}
