from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

from app.database import Base


class TrainerSchedule(Base):
    __tablename__ = "trainer_schedules"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day = Column(String, nullable=False)
    time = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day = Column(String, nullable=False)
    time = Column(String, nullable=False)
    status = Column(String, default="pending")
    notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())