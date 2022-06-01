import asyncio
from typing import Sequence

import httpx
from bson import ObjectId
from bson import errors as bson_errors
from supertokens_python.recipe.emailpassword.asyncio import sign_in
from supertokens_python.recipe.emailpassword.interfaces import (
    SignInWrongCredentialsErrorResult,
)


from app.supertokens_config import dot_env
from app.schemas import Article


def validate_objectid(id: str) -> bool:
    """Returns `True` if `id` is valid ObjectId id"""
    try:
        ObjectId(id)
    except bson_errors.InvalidId:
        return False
    else:
        return True


async def article_exists(article_id: str) -> bool:
    """Returns `True` if article with given `article_id` exists by calling newsscraper api"""
    response = await make_request(
        f"{dot_env.NEWSSCRAPER_API_URL}/api/v1/news/{article_id}"
    )

    return response.status_code == 200


async def make_request(url: str) -> httpx.Response:
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=60.0)) as client:
        response = await client.get(url)

    return response


async def get_article_by_id(article_id: str) -> httpx.Response:
    url = f"{dot_env.NEWSSCRAPER_API_URL}/api/v1/news/{article_id}"
    response = await make_request(url)

    if response.status_code != 200:
        raise httpx.RequestError(
            f"Error making request to {url!r}. {response.status_code}"
        )

    article = Article(**response.json())

    return article


async def fetch_user_bookmarks(ids: Sequence[str]):
    """Fetches user bookmarked articles by making get request to newsscraper API to get actual articles instead of `GetBookmarkModel`"""
    awaitables = [get_article_by_id(a_id) for a_id in ids]
    articles = await asyncio.gather(*awaitables)

    return articles


async def is_user_password_valid(email: str, password: str) -> bool:
    is_password_valid = await sign_in(email, password)
    return not isinstance(is_password_valid, SignInWrongCredentialsErrorResult)
