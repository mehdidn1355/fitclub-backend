from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TrainerPlan(Base):
    __tablename__ = "trainer_plans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    training_type = Column(String, default="online")
    location = Column(String, default="home")
    equipment = Column(String, default="none")
    music_playlist = Column(String, nullable=True)
    body_focus = Column(String, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")


class PlanItem(Base):
    __tablename__ = "plan_items"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("trainer_plans.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    day = Column(String, nullable=False)
    order = Column(Integer, default=1)
    sets = Column(Integer, default=3)
    reps = Column(Integer, default=12)
    weight = Column(Float, default=0)
    rest_seconds = Column(Integer, default=60)
    notes = Column(Text, nullable=True)

    plan = relationship("TrainerPlan", back_populates="items")
    exercise = relationship("Exercise")