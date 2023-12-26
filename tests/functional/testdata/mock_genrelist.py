import uuid

from ..settings import settings


genrelist = [
    {
        "_index": settings.index_genres,
        "_id": (id := str(uuid.uuid4())),
        "_source": {"uuid": id, "name": "Action"},
    }
    for _ in range(26)
]
