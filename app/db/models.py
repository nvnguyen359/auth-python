# Models: User, Camera, Order 
# app/db/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

# =========================
# USER MODEL
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="operator")  # admin, supervisor, operator
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ: 1 user có nhiều orders
    orders = relationship("Order", back_populates="user")


# =========================
# CAMERA MODEL
# =========================
class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    unique_id = Column(String, unique=True, index=True, nullable=False)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    rtsp_url = Column(Text)
    backend = Column(String(50))
    prefer_gst = Column(Integer, default=0)
    is_connected = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    device_path = Column(String(255))
    status = Column(String(50))
    os_index= Column(Integer, default=0)
    orders = relationship("Order", back_populates="camera")


# =========================
# ORDER MODEL
# =========================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    parent_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"))
    session_id = Column(String(100))
    code = Column(String(100), index=True)
    status = Column(String(20), default="packing")  # packing, closed, error
    created_at = Column(DateTime, default=datetime.utcnow)
    start_at = Column(DateTime)
    closed_at = Column(DateTime)
    path_avatar = Column(String(255))
    path_video = Column(String(255))
    order_metadata = Column(Text)
    note = Column(Text)
    user = relationship("User", back_populates="orders")
    camera = relationship("Camera", back_populates="orders")
    parent = relationship("Order", remote_side=[id])
