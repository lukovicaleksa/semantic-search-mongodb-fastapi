from typing import Optional, List, Any

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime


class MovieBaseSchema(BaseModel):
    title: str = Field(...)
    overview: str = Field(...)
    genres: Optional[List[str]] = Field(None)
    runtime: Optional[int] = Field(None)
    release_date: Optional[datetime] = Field(None)
    budget: Optional[int] = Field(None)
    revenue: Optional[int] = Field(None)


class MovieSchema(MovieBaseSchema):
    id: str = Field(..., alias='_id')

    def __init__(self, **data: Any):
        # convert ObjectID to str
        if isinstance(data.get('_id'), ObjectId):
            data['_id'] = str(data['_id'])

        super().__init__(**data)
