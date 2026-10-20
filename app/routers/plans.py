from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import random

from app.database import get_db
from app.models.trainer_plan import TrainerPlan, PlanItem
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.exercise import Exercise
# 👇 این ایمپورت‌ها بسیار مهم هستند و باید کامل باشند
from app.schemas.trainer_plan import (
    TrainerPlanCreate,
    TrainerPlanRequest,
    TrainerPlanResponse,
    PlanItemCreate,
    PlanItemResponse
)
from app.auth.dependencies import get_current_user, require_trainer

router = APIRouter(prefix="/api/plans", tags=["Trainer Plans"])

# ============================================
# مدل ورودی برای برنامه‌ساز
# ============================================
class GeneratePlanRequest(BaseModel):
    gender: str = Field(..., description="male یا female")
    age: int = Field(..., ge=12, le=90)
    height: float = Field(..., ge=100, le=250, description="قد به سانتی‌متر")
    current_weight: float = Field(..., ge=30, le=250, description="وزن فعلی به کیلوگرم")
    target_weight: float = Field(..., ge=30, le=250, description="وزن هدف به کیلوگرم")
    goal: str = Field(..., description="muscle, weight_loss, fitness, strength")
    level: str = Field(..., description="beginner, intermediate, advanced")
    days_per_week: int = Field(default=3, ge=2, le=6)
    equipment: str = Field(default="none", description="none, basic, full")

# ============================================
# فرمول‌های علمی
# ============================================
def calculate_bmr(gender, weight, height, age):
    if gender == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_tdee(bmr, level):
    activity_multiplier = {
        "beginner": 1.375,
        "intermediate": 1.55,
        "advanced": 1.725,
    }
    return bmr * activity_multiplier.get(level, 1.375)

def get_target_calories(tdee, goal):
    if goal == "weight_loss":
        return tdee - 500
    elif goal == "muscle":
        return tdee + 300
    return tdee

# ============================================
# API برنامه‌ساز هوشمند
# ============================================
@router.post("/generate", response_model=TrainerPlanResponse)
def generate_plan(
    req: GeneratePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ۱. محاسبات علمی
    bmr = calculate_bmr(req.gender, req.current_weight, req.height, req.age)
    tdee = calculate_tdee(bmr, req.level)
    target_cal = get_target_calories(tdee, req.goal)
    
    # ۲. تعیین گروه‌های عضلانی
    focus_groups = []
    if req.goal == "muscle":
        if req.gender == "male":
            focus_groups = ["سینه", "پشت", "پا", "سرشانه", "بازو"]
        else:
            focus_groups = ["پا", "سرشانه", "بازو", "شکم"]
    elif req.goal == "weight_loss":
        focus_groups = ["پا", "شکم", "کاردیو", "سینه"]
    elif req.goal == "strength":
        focus_groups = ["پا", "پشت", "سینه"]
    else:
        focus_groups = ["سینه", "پشت", "پا", "شکم"]

    # ۳. فیلتر حرکات
    difficulty_map = {
        "beginner": ["مبتدی"],
        "intermediate": ["مبتدی", "متوسط"],
        "advanced": ["متوسط", "پیشرفته"],
    }
    allowed_difficulties = difficulty_map.get(req.level, ["مبتدی"])
    
    if req.equipment == "none":
        allowed_equipment = ["none", "بدون وسیله"]
    elif req.equipment == "basic":
        allowed_equipment = ["none", "basic", "بدون وسیله", "وسایل ساده"]
    else:
        allowed_equipment = ["none", "basic", "full", "بدون وسیله", "وسایل ساده", "وسایل کامل"]

    exercises = db.query(Exercise).filter(
        Exercise.difficulty.in_(allowed_difficulties),
        Exercise.muscle_group.in_(focus_groups),
        Exercise.equipment_needed.in_(allowed_equipment)
    ).all()
    
    if not exercises:
        raise HTTPException(status_code=400, detail="حرکاتی با این مشخصات پیدا نشد. لطفاً تجهیزات یا سطح را تغییر دهید.")

    # ۴. ساخت برنامه
    plan_items = []
    day_names = ["روز ۱", "روز ۲", "روز ۳", "روز ۴", "روز ۵", "روز ۶"]
    
    for day_idx in range(req.days_per_week):
        day = day_names[day_idx]
        num_ex = 5 if req.goal == "muscle" else 4
        selected = random.sample(exercises, min(num_ex, len(exercises)))
        
        for order, ex in enumerate(selected, start=1):
            plan_items.append({
                "exercise_id": ex.id,
                "day": day,
                "order": order,
                "sets": 4 if req.goal == "muscle" else 3,
                "reps": 8 if req.goal == "muscle" else 15,
                "weight": 0,
                "rest_seconds": 90 if req.goal == "muscle" else 45,
                "notes": f"هدف کالری روزانه: {int(target_cal)}"
            })

    # ۵. ذخیره در دیتابیس
    plan_title = f"برنامه‌ی {req.goal} برای {req.gender} {req.age} ساله"
    new_plan = TrainerPlan(
        customer_id=current_user.id,
        trainer_id=1, 
        title=plan_title,
        description=f"برنامه‌ی هوشمند بر اساس آنالیز بدنی. هدف کالری: {int(target_cal)} kcal",
        body_focus=",".join(focus_groups),
        music_playlist="workout_hits",
    )
    db.add(new_plan)
    db.flush()

    for item in plan_items:
        db.add(PlanItem(plan_id=new_plan.id, **item))
    
    db.commit()
    db.refresh(new_plan)
    return new_plan

# ============================================
# بقیه endpointها
# ============================================
@router.get("/my", response_model=List[TrainerPlanResponse])
def my_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(TrainerPlan).filter(
        TrainerPlan.customer_id == current_user.id
    ).order_by(TrainerPlan.created_at.desc()).all()

@router.get("/incoming", response_model=List[TrainerPlanResponse])
def incoming_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    return db.query(TrainerPlan).filter(
        TrainerPlan.trainer_id == current_user.id
    ).order_by(TrainerPlan.created_at.desc()).all()

@router.post("/request", response_model=TrainerPlanResponse)
def request_plan(
    data: TrainerPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trainer = db.query(User).filter(User.id == data.trainer_id, User.role == UserRole.TRAINER).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="مربی یافت نشد")

    plan = TrainerPlan(
        customer_id=current_user.id,
        trainer_id=data.trainer_id,
        title=data.title,
        description=data.description,
        training_type=data.training_type,
        location=data.location,
        equipment=data.equipment,
        music_playlist=data.music_playlist,
        body_focus=data.body_focus,
        is_active=False 
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.get("/{plan_id}", response_model=TrainerPlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(TrainerPlan).filter(TrainerPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="برنامه یافت نشد")
    
    if current_user.role == UserRole.CUSTOMER and plan.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="دسترسی غیرمجاز")
        
    return plan

@router.put("/{plan_id}/items")
def update_plan_items(
    plan_id: int,
    items: List[PlanItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    plan = db.query(TrainerPlan).filter(TrainerPlan.id == plan_id, TrainerPlan.trainer_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="برنامه یافت نشد یا دسترسی ندارید")
    
    db.query(PlanItem).filter(PlanItem.plan_id == plan.id).delete()
    
    for item in items:
        db.add(PlanItem(plan_id=plan.id, **item.model_dump()))
        
    plan.is_active = True
    db.commit()
    return {"message": "برنامه با موفقیت آپدیت شد"}