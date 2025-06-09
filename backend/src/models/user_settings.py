from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserSettings(BaseModel):
    user_id: str
    subscription_tier: str = "free"  # free, basic, premium
    preferred_model: str = "gpt-3.5-turbo"  # gpt-3.5-turbo, gpt-4, claude-3-opus, claude-3-sonnet
    max_tokens_per_month: int = 100000
    tokens_used_this_month: int = 0
    documents_processed_this_month: int = 0
    last_token_reset: datetime = datetime.now()
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "subscription_tier": "basic",
                "preferred_model": "gpt-3.5-turbo",
                "max_tokens_per_month": 100000,
                "tokens_used_this_month": 5000,
                "documents_processed_this_month": 2,
                "last_token_reset": "2024-03-20T00:00:00Z",
                "created_at": "2024-03-20T00:00:00Z",
                "updated_at": "2024-03-20T00:00:00Z"
            }
        } 