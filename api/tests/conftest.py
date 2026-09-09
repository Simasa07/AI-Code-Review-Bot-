import os

# Use a throwaway local database for tests instead of the real Postgres one.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_api.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "")
