import uuid

from ..settings import settings


personlist = [
    {
        "_index": settings.index_persons,
        "_id": (id := str(uuid.uuid4())),
        "_source": {
            "uuid": id,
            "full_name": "Andrew Jackson",
            "films": [
                {"uuid": "b2540995-0f91-4db1-99ed-dd7bcb3976d9", "roles": ["actor"]}
            ],
        },
    }
    for _ in range(60)
]
