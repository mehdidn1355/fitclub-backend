from pydantic import BaseModel
from typing import Optional


class ExerciseBase(BaseModel):
    name: str
    name_en: str
    muscle_group: str
    description: Optional[str] = None
    animation_key: str
    difficulty: str = "مبتدی"
    icon: str = "🏋️"
    default_sets: int = 3
    default_reps: int = 12
    rest_seconds: int = 60
    equipment_needed: str = "none"  # ← این خط مهمه


class ExerciseResponse(ExerciseBase):
    id: int
    related_product_ids: str = ""

    class Config:
        from_attributes = True