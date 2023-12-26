import sys
import logging

import backoff
import elasticsearch

sys.path.append("..")
from settings import settings


def backoff_message(detail):
    logging.getLogger("my-logger").warning("Elasticsearch is not ready. Waiting...")


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=elasticsearch.ConnectionError,
    on_backoff=backoff_message,
    max_time=settings.elastic_waiter_timelimit,
)
def wait_for_es(es):
    if not es.ping():
        raise elasticsearch.ConnectionError("Error")


if __name__ == "__main__":
    es = elasticsearch.Elasticsearch(
        hosts=[f"{settings.elastic_host}:{settings.elastic_port}"]
    )
    wait_for_es(es)
    logging.getLogger("my-logger").warning("Elasticsearch is ready")
