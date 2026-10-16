from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.exercise import ExerciseResponse


class PlanItemCreate(BaseModel):
    exercise_id: int
    day: str
    order: int = 1
    sets: int = 3
    reps: int = 12
    weight: float = 0
    rest_seconds: int = 60
    notes: Optional[str] = None


class PlanItemResponse(BaseModel):
    id: int
    exercise_id: int
    day: str
    order: int
    sets: int
    reps: int
    weight: float
    rest_seconds: int
    notes: Optional[str] = None
    exercise: Optional[ExerciseResponse] = None

    class Config:
        from_attributes = True


class TrainerPlanCreate(BaseModel):
    customer_id: Optional[int] = None
    trainer_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    training_type: str = "online"
    location: str = "home"
    equipment: str = "none"
    music_playlist: Optional[str] = None
    body_focus: str = ""
    items: List[PlanItemCreate] = []


class TrainerPlanRequest(BaseModel):
    """درخواست کاربر عادی برای دریافت برنامه."""
    trainer_id: int
    title: str
    description: Optional[str] = None
    training_type: str = "online"
    location: str = "home"
    equipment: str = "none"
    music_playlist: Optional[str] = None
    body_focus: str = ""


class TrainerPlanResponse(BaseModel):
    id: int
    customer_id: int
    trainer_id: int
    title: str
    description: Optional[str] = None
    training_type: str
    location: str
    equipment: str
    music_playlist: Optional[str] = None
    body_focus: str = ""
    is_active: bool
    created_at: datetime
    items: List[PlanItemResponse] = []

    class Config:
        from_attributes = True