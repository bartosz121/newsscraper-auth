from bson import ObjectId
from datetime import datetime

from pydantic import BaseModel, Field

from app.py_object_id import PyObjectId


class GetBookmarkModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    article_id: str

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class GetBookmarkModelPaginated(BaseModel):
    # list with article ids
    result: list[GetBookmarkModel]
    hasNext: bool
    pageNumber: int

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class CreateBookmarkModel(BaseModel):
    article_id: str


class DeleteBookmarkModel(BaseModel):
    document_id: str
