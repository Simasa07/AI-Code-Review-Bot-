import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_worker.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("GOOGLE_API_KEY", "")
os.environ.setdefault("GITHUB_TOKEN", "")
