import httpx
from bson import ObjectId
from bson import errors as bson_errors

from app.supertokens_config import dot_env


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
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{dot_env.NEWSSCRAPER_API_URL}/api/v1/news/{article_id}"
        )

    return response.status_code == 200
