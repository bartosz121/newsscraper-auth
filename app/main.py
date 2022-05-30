import motor.motor_asyncio
from bson import ObjectId
from fastapi import FastAPI, Depends, status, HTTPException
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware

from supertokens_python import init, get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.schemas import (
    CreateBookmarkModel,
    DeleteBookmarkModel,
    GetBookmarkModel,
    GetBookmarkModelPaginated,
)

from app.supertokens_config import dot_env, app_info, supertokens_config
from app.utils import article_exists, validate_objectid


# Supertokens
init(
    app_info=app_info,
    supertokens_config=supertokens_config,
    framework="fastapi",
    recipe_list=[
        session.init(),  # initializes session features
        emailpassword.init(),
    ],
    mode="asgi",  # use wsgi if you are running using gunicorn
)

# Fast api
f_app = FastAPI()
f_app.add_middleware(get_middleware())

app = CORSMiddleware(
    app=f_app,
    allow_origins=[
        dot_env.WEBSITE_DOMAIN,
    ],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)

# Db
client = motor.motor_asyncio.AsyncIOMotorClient(dot_env.MONGO_URI)
db = client[dot_env.MONGO_DB_NAME]
coll = db["bookmarks"]

# Bookmark post
@f_app.get("/bookmark", response_model=GetBookmarkModelPaginated)
async def show_bookmarks(
    session: SessionContainer = Depends(verify_session()),
    page: int = 1,
    page_size: int = 10,
):
    user_id = session.get_user_id()
    item_count = await coll.count_documents({"user_id": user_id})
    offset = (page - 1) * page_size

    user_bookmarks = (
        await coll.find({"user_id": user_id}).skip(offset).to_list(page_size)
    )

    data = {
        "result": user_bookmarks,
        "hasNext": (offset + page_size) < item_count,
        "pageNumber": page,
    }

    return data


@f_app.post(
    "/bookmark", status_code=status.HTTP_201_CREATED, response_model=GetBookmarkModel
)
async def add_bookmark(
    article_info: CreateBookmarkModel,
    session: SessionContainer = Depends(verify_session()),
):
    if not validate_objectid(article_info.article_id):
        raise HTTPException(status_code=400, detail="Invalid document id")

    if not await article_exists(article_info.article_id):
        raise HTTPException(
            status_code=404,
            detail=f"Article with id {article_info.article_id!r} not found",
        )

    user_id = session.get_user_id()

    # skip if already added
    if check := await coll.find_one(
        {"user_id": user_id, "article_id": article_info.article_id}
    ):
        return check

    new_bookmark = await coll.insert_one(
        {
            "article_id": article_info.article_id,
            "user_id": user_id,
        }
    )
    created_bookmark = await coll.find_one({"_id": new_bookmark.inserted_id})

    return created_bookmark


@f_app.delete(
    "/bookmark", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def delete_bookmark(
    delete_model: DeleteBookmarkModel,
    session: SessionContainer = Depends(verify_session()),
):
    if not validate_objectid(delete_model.document_id):
        raise HTTPException(status_code=400, detail="Invalid document id")

    bson_id = ObjectId(delete_model.document_id)
    bookmark = await coll.find_one({"_id": bson_id})

    if not bookmark:
        raise HTTPException(
            status_code=404,
            detail=f"Bookmark with id {delete_model.document_id!r} not found",
        )

    await coll.delete_one({"_id": bson_id})
    return
