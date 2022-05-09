from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python import init, get_all_cors_headers
from supertokens_python.recipe import emailpassword, session

from .supertokens_config import dot_env, app_info, supertokens_config


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

app = FastAPI()
app.add_middleware(get_middleware())

app = CORSMiddleware(
    app=app,
    allow_origins=[
        dot_env.WEBSITE_DOMAIN,
    ],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)
