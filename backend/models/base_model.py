"""Simplified base database model without BSON ObjectId"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BaseDocument(BaseModel):
    """Simplified base model with string IDs to avoid BSON issues"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override dict method for consistent serialization"""
        data = super().dict(**kwargs)
        return data
