import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Pulled from environment so the same code works locally (docker-compose)
# and later in Kubernetes (via ConfigMap/Secret) without any code changes.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://taskflow:taskflow@localhost:5432/taskflow",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
