from typing import Optional
from bson import ObjectId
from datetime import datetime

from pydantic import BaseModel, Field

from app.py_object_id import PyObjectId


class Article(BaseModel):
    id: str
    title: str
    source_name: str
    source_unique_id: str
    url: str
    created: datetime
    img_url: Optional[str]
    description: Optional[str]


class GetBookmarkModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    article_id: str
    created: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class GetBookmarkModelPaginated(BaseModel):
    # list with article ids
    result: list[Article]
    hasNext: bool
    pageNumber: int

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class CreateBookmarkModel(BaseModel):
    article_id: str


class DeleteBookmarkModel(BaseModel):
    article_id: str


class GetBookmarkCheckRequestModel(BaseModel):
    article_id: str


class GetBookmarkCheckResponseModel(BaseModel):
    is_bookmarked: bool


class ChangePasswordRequestModel(BaseModel):
    old_password: str
    new_password: str


class ChangePasswordResponseModel(BaseModel):
    msg: str


class ChangeEmailRequestModel(BaseModel):
    new_email: str
    password: str


class ChangeEmailResponseModel(BaseModel):
    msg: str
