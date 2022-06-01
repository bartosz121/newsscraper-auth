import motor.motor_asyncio
from datetime import datetime
from fastapi import FastAPI, Depends, status, HTTPException
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware

from supertokens_python import init, get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.emailpassword.asyncio import (
    get_user_by_id,
    sign_in,
    update_email_or_password,
)
from supertokens_python.recipe.emailpassword.interfaces import (
    SignInWrongCredentialsErrorResult,
)

from app.schemas import (
    ChangeEmailRequestModel,
    ChangeEmailResponseModel,
    ChangePasswordRequestModel,
    ChangePasswordResponseModel,
    CreateBookmarkModel,
    DeleteBookmarkModel,
    GetBookmarkCheckRequestModel,
    GetBookmarkCheckResponseModel,
    GetBookmarkModel,
    GetBookmarkModelPaginated,
)

from app.supertokens_config import dot_env, app_info, supertokens_config
from app.utils import (
    article_exists,
    fetch_user_bookmarks,
    validate_objectid,
    is_user_password_valid,
)


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

# Change password
@f_app.post("/change_password", response_model=ChangePasswordResponseModel)
async def change_password(
    data: ChangePasswordRequestModel,
    session: SessionContainer = Depends(verify_session()),
):
    user_id = session.get_user_id()
    users_info = await get_user_by_id(user_id)

    if users_info is None:
        raise HTTPException(status_code=400, detail=f"User info not found. Try again")

    if not await is_user_password_valid(users_info.email, data.old_password):
        raise HTTPException(status_code=400, detail="Wrong old password")

    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=400,
            detail=f"New password cannot be the same as your old password",
        )

    status = await update_email_or_password(user_id, password=data.new_password)

    if status.is_ok:
        await session.revoke_session()
        return ChangePasswordResponseModel(msg="ok")

    raise HTTPException(status_code=500, detail="Unknown error. Please try again")


# Change email
@f_app.post("/change_email", response_model=ChangeEmailResponseModel)
async def change_email(
    data: ChangeEmailRequestModel, session: SessionContainer = Depends(verify_session())
):
    user_id = session.get_user_id()
    users_info = await get_user_by_id(user_id)

    if users_info is None:
        raise HTTPException(status_code=400, detail=f"User info not found. Try again")

    if not await is_user_password_valid(users_info.email, data.password):
        raise HTTPException(status_code=400, detail="Wrong password")

    if data.new_email == users_info.email:
        raise HTTPException(
            status_code=400,
            detail=f"New email address cannot be the same as your old email address",
        )

    status = await update_email_or_password(user_id, email=data.new_email)

    if status.is_ok:
        return ChangeEmailResponseModel(msg="ok")

    if status.is_email_already_exists_error:
        raise HTTPException(status_code=400, detail=f"Email already exists")

    raise HTTPException(status_code=500, detail="Unknown error. Please try again")


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
        await coll.find({"user_id": user_id})
        .sort("created", -1)
        .skip(offset)
        .to_list(page_size)
    )

    articles = await fetch_user_bookmarks(
        tuple(bookmark["article_id"] for bookmark in user_bookmarks)
    )

    data = {
        "result": articles,
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
            "created": datetime.utcnow(),
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
    user_id = session.get_user_id()
    bookmark = await coll.find_one(
        {"user_id": user_id, "article_id": delete_model.article_id}
    )

    if not bookmark:
        raise HTTPException(
            status_code=404,
            detail=f"Bookmark not found",
        )

    await coll.delete_one({"_id": bookmark["_id"]})
    return


@f_app.post("/bookmark/check", response_model=GetBookmarkCheckResponseModel)
async def check_if_bookmarked(
    req_data: GetBookmarkCheckRequestModel,
    session: SessionContainer = Depends(verify_session()),
):
    if not await article_exists(req_data.article_id):
        raise HTTPException(
            status_code=404,
            detail=f"Article with id {req_data.article_id!r} not found",
        )

    user_id = session.get_user_id()

    check = await coll.find_one({"user_id": user_id, "article_id": req_data.article_id})

    return GetBookmarkCheckResponseModel(is_bookmarked=bool(check))
