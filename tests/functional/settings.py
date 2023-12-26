import os

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    base_api_url: str = "http://fastapi:8000/api/v1"

    # настройки redis
    redis_host: str = "redis"
    redis_port: int = 6379

    # настройки elastic
    elastic_host: str = "http://elastic"
    elastic_port: int = 9200
    index_movies: str = "movies"
    index_persons: str = "persons"
    index_genres: str = "genres"

    # настройки для waiters
    elastic_waiter_timelimit: int = 300
    redis_waiter_timelimit: int = 300


settings = Settings()

tests_run_mode = os.environ.get("TESTS_RUN_LOCALLY")
if tests_run_mode in ["true", "TRUE", "yes", "YES"]:
    settings.base_api_url = "http://127.0.0.1:8000/api/v1"
    settings.redis_host = "127.0.0.1"
    settings.elastic_host = "http://127.0.0.1"
