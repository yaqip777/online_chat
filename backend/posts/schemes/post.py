from datetime import datetime
from pydantic import BaseModel

class PostResponseSchema(BaseModel):
    id: int
    text: str | None
    image_url: str | None
    video_url: str | None
    created_at: datetime
    user_id: int

    model_config = {
        "from_attributes": True
    }