import uuid

from ..settings import settings


filmlist = [
    {
        "_index": settings.index_movies,
        "_id": (id := str(uuid.uuid4())),
        "_source": {
            "uuid": id,
            "title": "Star Ocean: Till the End of Time",
            "imdb_rating": 7.9,
            "description": "A young 19 year old college student...",
            "genre": [
                {"uuid": "120a21cf-9097-479e-904a-13dd7198c1dd", "name": "Adventure"},
                {"uuid": "1cacff68-643e-4ddd-8f57-84b62538081a", "name": "Drama"},
                {"uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"},
            ],
            "actors": [
                {
                    "uuid": "3c9dc3af-f6ee-407e-8e00-b10614843511",
                    "full_name": "Sôichirô Hoshi",
                },
                {
                    "uuid": "6074645a-a40d-4766-a3e4-e48294f64ee7",
                    "full_name": "Yu Asakawa",
                },
                {
                    "uuid": "71fdd822-223c-4a1c-b0e1-9322257284e9",
                    "full_name": "Isshin Chiba",
                },
                {
                    "uuid": "f6d82402-367d-4575-a64f-9e40a691f9de",
                    "full_name": "Atsuko Enomoto",
                },
            ],
            "writers": [
                {
                    "uuid": "112915df-c5eb-4eb5-85c7-742aabd2a408",
                    "full_name": "Hiroshi Ogawa",
                },
                {
                    "uuid": "d0d8c214-c043-4757-8621-a307e1b7491d",
                    "full_name": "Yoshiharu Gotanda",
                },
            ],
            "directors": [
                {
                    "uuid": "d0d8c214-c043-4757-8621-a307e1b7491d",
                    "full_name": "Yoshiharu Gotanda",
                }
            ],
        },
    }
    for _ in range(60)
]
