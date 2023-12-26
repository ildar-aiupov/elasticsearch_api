#!/bin/bash

cd /app/utils
python wait_for_es.py
python wait_for_redis.py

cd /app/src
pytest .
