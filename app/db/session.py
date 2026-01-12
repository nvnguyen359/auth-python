# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SỬA LỖI: Đổi settings.db_url thành settings.DB_URL để khớp với config.py
engine = create_engine(
    settings.DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DB_URL else {},
    pool_pre_ping=True,
)

# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency cho FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()