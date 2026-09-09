import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# The API only ever *sends* jobs, it never runs them itself.
celery_client = Celery("review_bot_client", broker=REDIS_URL, backend=REDIS_URL)
