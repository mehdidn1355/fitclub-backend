from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.nutrition import NutritionPlan, MealPlan, Supplement
from app.models.user import User, UserRole
from app.schemas.nutrition import (
    NutritionPlanCreate,
    NutritionPlanResponse,
)
from app.auth.dependencies import get_current_user, require_trainer

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])


@router.post("", response_model=NutritionPlanResponse, status_code=201)
def create_nutrition_plan(
    plan_data: NutritionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    """مربی برنامه‌ی غذایی می‌سازه."""
    # بررسی مشتری
    customer = db.query(User).filter(User.id == plan_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # چک کن قبلاً برنامه‌ی غذایی داره
    existing = db.query(NutritionPlan).filter(
        NutritionPlan.customer_id == plan_data.customer_id,
        NutritionPlan.is_active == True,
    ).first()

    if existing:
        # حذف قبلی
        db.delete(existing)
        db.commit()

    # ساخت پلن
    plan = NutritionPlan(
        customer_id=plan_data.customer_id,
        trainer_id=current_user.id,
        title=plan_data.title,
        description=plan_data.description,
        daily_calories=plan_data.daily_calories,
        protein_grams=plan_data.protein_grams,
        carbs_grams=plan_data.carbs_grams,
        fat_grams=plan_data.fat_grams,
        water_liters=plan_data.water_liters,
        notes=plan_data.notes,
    )
    db.add(plan)
    db.flush()

    # وعده‌ها
    for meal in plan_data.meals:
        db.add(MealPlan(nutrition_plan_id=plan.id, **meal.model_dump()))

    # مکمل‌ها
    for supp in plan_data.supplements:
        db.add(Supplement(nutrition_plan_id=plan.id, **supp.model_dump()))

    db.commit()
    db.refresh(plan)
    return plan


@router.get("/my", response_model=NutritionPlanResponse)
def my_nutrition_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """برنامه‌ی غذایی کاربر فعلی."""
    if current_user.role == UserRole.TRAINER:
        # مربی: آخرین برنامه‌ای که ساخته
        plan = (
            db.query(NutritionPlan)
            .filter(NutritionPlan.trainer_id == current_user.id)
            .order_by(NutritionPlan.created_at.desc())
            .first()
        )
    else:
        # مشتری
        plan = (
            db.query(NutritionPlan)
            .filter(
                NutritionPlan.customer_id == current_user.id,
                NutritionPlan.is_active == True,
            )
            .first()
        )

    if not plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")
    return plan


@router.get("/customer/{customer_id}", response_model=NutritionPlanResponse)
def customer_nutrition_plan(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    """مربی برنامه‌ی غذایی یه شاگرد رو می‌بینه."""
    plan = (
        db.query(NutritionPlan)
        .filter(
            NutritionPlan.customer_id == customer_id,
            NutritionPlan.is_active == True,
        )
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")
    return plan