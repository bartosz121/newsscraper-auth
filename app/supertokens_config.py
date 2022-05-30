import os
from typing import NamedTuple

from supertokens_python import InputAppInfo, SupertokensConfig
from dotenv import load_dotenv

load_dotenv()


class DotEnv(NamedTuple):
    APP_NAME: str
    API_DOMAIN: str
    WEBSITE_DOMAIN: str
    CONNECTION_URI: str
    API_KEY: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    NEWSSCRAPER_API_URL: str


dot_env = DotEnv(
    os.getenv("APP_NAME"),
    os.getenv("API_DOMAIN"),
    os.getenv("WEBSITE_DOMAIN"),
    os.getenv("CONNECTION_URI"),
    os.getenv("API_KEY"),
    os.getenv("MONGO_URI"),
    os.getenv("MONGO_DB_NAME"),
    os.getenv("NEWSSCRAPER_API_URL"),
)


app_info = InputAppInfo(
    app_name=dot_env.APP_NAME,
    api_domain=dot_env.API_DOMAIN,
    website_domain=dot_env.WEBSITE_DOMAIN,
    api_base_path="/auth",
    website_base_path="/auth",
)

supertokens_config = SupertokensConfig(
    connection_uri=dot_env.CONNECTION_URI,
    api_key=dot_env.API_KEY,
)
