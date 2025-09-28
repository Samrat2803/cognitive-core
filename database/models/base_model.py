"""Base database model with common fields and methods"""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseDocument(BaseModel):
    """Base model with common fields"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override dict method to handle ObjectId serialization"""
        data = super().dict(**kwargs)
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return data
