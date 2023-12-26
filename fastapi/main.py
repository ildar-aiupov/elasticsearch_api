from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genres, persons
from core.config import settings
from db import current_storage, current_cache
from db.elastic import AsyncElasticSearchEngine
from db.redis import AsyncRedisCacheEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    current_cache.current_cache = AsyncRedisCacheEngine()
    current_storage.current_storage = AsyncElasticSearchEngine()
    yield
    await current_storage.current_storage.close()
    await current_cache.current_cache.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(
    films.person_in_films_router,
    prefix="/api/v1/persons/{person_id}/film",
    tags=["persons"],
)
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
