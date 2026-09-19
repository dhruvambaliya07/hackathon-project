import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("AI_API_KEY", "test-key")
os.environ.setdefault("AI_MODEL", "test-model")
os.environ.setdefault("EMBEDDING_MODEL", "test-embedding")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")