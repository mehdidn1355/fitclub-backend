from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    daily_calories = Column(Integer, default=2000)
    protein_grams = Column(Integer, default=150)
    carbs_grams = Column(Integer, default=200)
    fat_grams = Column(Integer, default=70)
    water_liters = Column(Float, default=2.5)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meals = relationship("MealPlan", back_populates="nutrition_plan", cascade="all, delete-orphan")
    supplements = relationship("Supplement", back_populates="nutrition_plan", cascade="all, delete-orphan")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"), nullable=False)
    meal_type = Column(String, nullable=False)  # صبحانه، ناهار، شام، میان‌وعده
    time = Column(String, nullable=True)  # "08:00"
    foods = Column(Text, nullable=False)  # "۳ عدد تخم‌مرغ + نان سبوس‌دار"
    calories = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    order = Column(Integer, default=1)

    nutrition_plan = relationship("NutritionPlan", back_populates="meals")


class Supplement(Base):
    __tablename__ = "supplements"

    id = Column(Integer, primary_key=True, index=True)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"), nullable=False)
    name = Column(String, nullable=False)  # "پروتئین وی"
    dosage = Column(String, nullable=False)  # "۲ اسکوپ"
    timing = Column(String, nullable=False)  # "بعد از تمرین"
    category = Column(String, default="supplement")  # supplement, vitamin, mineral
    icon = Column(String, default="🥤")
    notes = Column(Text, nullable=True)
    related_product_ids = Column(String, default="")
    order = Column(Integer, default=1)

    nutrition_plan = relationship("NutritionPlan", back_populates="supplements")