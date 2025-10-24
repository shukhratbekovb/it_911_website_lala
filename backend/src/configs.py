import os

import pytz

from dotenv import load_dotenv

import redis.asyncio as aioredis

from functools import lru_cache

load_dotenv()

TIMEZONE = pytz.timezone('Asia/Tashkent')

DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TIME = os.getenv("ACCESS_TIME")
REFRESH_TIME = os.getenv("REFRESH_TIME")


BOT_SECRET = os.getenv("BOT_SECRET")

@lru_cache
def get_redis() -> aioredis.Redis:
    return aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True,
    )
