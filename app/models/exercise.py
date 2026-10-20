from sqlalchemy import Column, Integer, String, Text, Float
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    muscle_group = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    animation_key = Column(String, nullable=False)
    difficulty = Column(String, default="مبتدی")
    icon = Column(String, default="🏋️")
    default_sets = Column(Integer, default=3)
    default_reps = Column(Integer, default=12)
    rest_seconds = Column(Integer, default=60)
    calories_per_minute = Column(Float, default=5.0)
    related_product_ids = Column(String, default="")
    equipment_needed = Column(String, default="none")  # ← این خط مهمه