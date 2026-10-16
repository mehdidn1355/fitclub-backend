from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MealPlanCreate(BaseModel):
    meal_type: str
    time: Optional[str] = None
    foods: str
    calories: int = 0
    notes: Optional[str] = None
    order: int = 1


class MealPlanResponse(MealPlanCreate):
    id: int

    class Config:
        from_attributes = True


class SupplementCreate(BaseModel):
    name: str
    dosage: str
    timing: str
    category: str = "supplement"
    icon: str = "🥤"
    notes: Optional[str] = None
    related_product_ids: str = ""
    order: int = 1


class SupplementResponse(SupplementCreate):
    id: int

    class Config:
        from_attributes = True


class NutritionPlanCreate(BaseModel):
    customer_id: int
    title: str
    description: Optional[str] = None
    daily_calories: int = 2000
    protein_grams: int = 150
    carbs_grams: int = 200
    fat_grams: int = 70
    water_liters: float = 2.5
    notes: Optional[str] = None
    meals: List[MealPlanCreate] = []
    supplements: List[SupplementCreate] = []


class NutritionPlanResponse(BaseModel):
    id: int
    customer_id: int
    trainer_id: int
    title: str
    description: Optional[str] = None
    daily_calories: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    water_liters: float
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    meals: List[MealPlanResponse] = []
    supplements: List[SupplementResponse] = []

    class Config:
        from_attributes = True