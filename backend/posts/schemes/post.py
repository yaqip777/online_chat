from datetime import datetime
from pydantic import BaseModel

class PostCreateSchema(BaseModel):
    text: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Salom, bu mening birinchi postim!"
                }
            ]
        }
    }

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