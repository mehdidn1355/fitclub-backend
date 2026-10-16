from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.trainer_plan import TrainerPlan, PlanItem
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.trainer_plan import (
    TrainerPlanCreate,
    TrainerPlanRequest,
    TrainerPlanResponse,
    PlanItemCreate,
)
from app.auth.dependencies import get_current_user, require_trainer

router = APIRouter(prefix="/api/plans", tags=["Trainer Plans"])


@router.post("/request", response_model=TrainerPlanResponse, status_code=201)
def request_plan(
    plan_data: TrainerPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """کاربر عادی درخواست برنامه می‌ده."""
    trainer = db.query(User).filter(
        User.id == plan_data.trainer_id,
        User.role == UserRole.TRAINER,
    ).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    plan = TrainerPlan(
        customer_id=current_user.id,
        trainer_id=plan_data.trainer_id,
        title=plan_data.title,
        description=plan_data.description,
        training_type=plan_data.training_type,
        location=plan_data.location,
        equipment=plan_data.equipment,
        music_playlist=plan_data.music_playlist,
        body_focus=plan_data.body_focus,
        is_active=True,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("", response_model=TrainerPlanResponse, status_code=201)
def create_plan(
    plan_data: TrainerPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    """مربی برنامه‌ی جدید می‌سازه."""
    customer = db.query(User).filter(User.id == plan_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    plan = TrainerPlan(
        customer_id=plan_data.customer_id,
        trainer_id=current_user.id,
        title=plan_data.title,
        description=plan_data.description,
        training_type=plan_data.training_type,
        location=plan_data.location,
        equipment=plan_data.equipment,
        music_playlist=plan_data.music_playlist,
        body_focus=plan_data.body_focus,
    )
    db.add(plan)
    db.flush()

    for item in plan_data.items:
        db.add(PlanItem(plan_id=plan.id, **item.model_dump()))

    db.commit()
    db.refresh(plan)
    return plan


# 🆕 دریافت درخواست‌های دریافتی
@router.get("/incoming", response_model=List[TrainerPlanResponse])
def incoming_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    """درخواست‌های کاربران برای این مربی."""
    return (
        db.query(TrainerPlan)
        .filter(TrainerPlan.trainer_id == current_user.id)
        .order_by(TrainerPlan.created_at.desc())
        .all()
    )


# 🆕 ذخیره‌ی حرکات برنامه
@router.put("/{plan_id}/items", response_model=TrainerPlanResponse)
def update_plan_items(
    plan_id: int,
    items: List[PlanItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    """مربی حرکات برنامه رو ذخیره می‌کنه."""
    plan = db.query(TrainerPlan).filter(TrainerPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # بررسی دسترسی
    if plan.trainer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")

    # پاک کردن حرکات قبلی
    db.query(PlanItem).filter(PlanItem.plan_id == plan_id).delete()

    # اضافه کردن حرکات جدید
    for item in items:
        db.add(PlanItem(plan_id=plan_id, **item.model_dump()))

    db.commit()
    db.refresh(plan)
    return plan


@router.get("/my", response_model=List[TrainerPlanResponse])
def my_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """برنامه‌های کاربر فعلی."""
    if current_user.role == UserRole.TRAINER:
        return (
            db.query(TrainerPlan)
            .filter(TrainerPlan.trainer_id == current_user.id)
            .order_by(TrainerPlan.created_at.desc())
            .all()
        )
    else:
        return (
            db.query(TrainerPlan)
            .filter(TrainerPlan.customer_id == current_user.id)
            .order_by(TrainerPlan.created_at.desc())
            .all()
        )


@router.get("/{plan_id}", response_model=TrainerPlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(TrainerPlan).filter(TrainerPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if (
        plan.customer_id != current_user.id
        and plan.trainer_id != current_user.id
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return plan


@router.get("/{plan_id}/suggested-products")
def get_suggested_products(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """محصولات مرتبط با حرکات این برنامه."""
    plan = db.query(TrainerPlan).filter(TrainerPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    product_ids = set()
    for item in plan.items:
        if item.exercise and item.exercise.related_product_ids:
            for pid in item.exercise.related_product_ids.split(","):
                pid = pid.strip()
                if pid.isdigit():
                    product_ids.add(int(pid))

    if not product_ids:
        products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .order_by(Product.rating.desc())
            .limit(3)
            .all()
        )
    else:
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "icon": p.icon,
            "rating": p.rating,
            "category": p.category,
        }
        for p in products
    ]