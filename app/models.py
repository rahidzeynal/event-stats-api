from pydantic import BaseModel, field_validator
from datetime import datetime, timezone

class Event(BaseModel):
    timestamp: datetime
    value: float
    
    @field_validator('timestamp')
    @classmethod
    def ensure_utc_timezone(cls, v: datetime) -> datetime:
        """Ensure timestamp is timezone-aware and in UTC"""
        if v.tzinfo is None:
            # If naive datetime, assume it's UTC
            return v.replace(tzinfo=timezone.utc)
        # If already timezone-aware, convert to UTC
        return v.astimezone(timezone.utc)
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-21T12:00:00Z",
                "value": 42.5
            }
        }