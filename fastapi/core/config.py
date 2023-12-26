import os
from logging import config as logging_config

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)
load_dotenv()


class Settings(BaseSettings):
    project_name: str = "movies"
    not_found_message: str = "Required resource is not found"
    default_persons_pagin_page_size: int = 50
    default_films_pagin_page_size: int = 50
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # настройки redis
    redis_host: str = "redis"
    redis_port: int = 6379
    film_cache_time: int = 30
    person_cache_time: int = 30
    genre_cache_time: int = 30

    # настройки elastic
    elastic_host: str = "http://elastic"
    elastic_port: int = 9200
    index_movies: str = "movies"
    index_persons: str = "persons"
    index_genres: str = "genres"


settings = Settings()
