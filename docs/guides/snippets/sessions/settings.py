# settings.py
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

SESSIONS = {"secret_key": config("SECRET_KEY", cast=Secret)}
