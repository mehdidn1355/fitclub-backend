from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.models.booking import Booking
from app.models.trainer_plan import TrainerPlan
from app.models.nutrition import NutritionPlan
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============ Helper: نام ماه فارسی ============
def _get_persian_month(month_num: int) -> str:
    months = {
        1: "ژانویه",
        2: "فوریه",
        3: "مارس",
        4: "آپریل",
        5: "مِی",
        6: "ژوئن",
        7: "جولای",
        8: "آگوست",
        9: "سپتامبر",
        10: "اکتبر",
        11: "نوامبر",
        12: "دسامبر",
    }
    return months.get(month_num, str(month_num))


# ============ آمار کلی ============
@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """آمار کلی باشگاه."""
    try:
        total_members = (
            db.query(func.count(User.id))
            .filter(User.role == UserRole.CUSTOMER)
            .scalar()
            or 0
        )
        total_trainers = (
            db.query(func.count(User.id))
            .filter(User.role == UserRole.TRAINER)
            .scalar()
            or 0
        )
        total_courses = db.query(func.count(Course.id)).scalar() or 0
        total_products = db.query(func.count(Product.id)).scalar() or 0
        total_orders = db.query(func.count(Order.id)).scalar() or 0
        total_bookings = db.query(func.count(Booking.id)).scalar() or 0
        total_plans = db.query(func.count(TrainerPlan.id)).scalar() or 0
        total_nutrition = db.query(func.count(NutritionPlan.id)).scalar() or 0

        total_revenue = (
            db.query(func.coalesce(func.sum(Order.total), 0))
            .filter(Order.status != OrderStatus.CANCELLED)
            .scalar()
            or 0
        )

        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_orders = (
            db.query(func.count(Order.id))
            .filter(Order.created_at >= today_start)
            .scalar()
            or 0
        )
        today_revenue = (
            db.query(func.coalesce(func.sum(Order.total), 0))
            .filter(
                Order.created_at >= today_start,
                Order.status != OrderStatus.CANCELLED,
            )
            .scalar()
            or 0
        )

        month_start = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        month_revenue = (
            db.query(func.coalesce(func.sum(Order.total), 0))
            .filter(
                Order.created_at >= month_start,
                Order.status != OrderStatus.CANCELLED,
            )
            .scalar()
            or 0
        )
        month_orders = (
            db.query(func.count(Order.id))
            .filter(Order.created_at >= month_start)
            .scalar()
            or 0
        )

        return {
            "total_members": total_members,
            "total_trainers": total_trainers,
            "total_courses": total_courses,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_bookings": total_bookings,
            "total_plans": total_plans,
            "total_nutrition": total_nutrition,
            "total_revenue": float(total_revenue),
            "today_orders": today_orders,
            "today_revenue": float(today_revenue),
            "month_orders": month_orders,
            "month_revenue": float(month_revenue),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در آمار: {str(e)}")


# ============ درآمد ۱۲ ماه اخیر ============
@router.get("/reports/revenue")
def get_revenue_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """درآمد ۱۲ ماه اخیر."""
    try:
        now = datetime.utcnow()
        months_data = []

        for i in range(11, -1, -1):
            # محاسبه‌ی ماه با استفاده از replace و سال/ماه
            year = now.year
            month = now.month - i
            while month <= 0:
                month += 12
                year -= 1

            month_start = datetime(year, month, 1)

            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)

            revenue = (
                db.query(func.coalesce(func.sum(Order.total), 0))
                .filter(
                    Order.created_at >= month_start,
                    Order.created_at < next_month,
                    Order.status != OrderStatus.CANCELLED,
                )
                .scalar()
                or 0
            )

            orders_count = (
                db.query(func.count(Order.id))
                .filter(
                    Order.created_at >= month_start,
                    Order.created_at < next_month,
                )
                .scalar()
                or 0
            )

            months_data.append({
                "month": month_start.strftime("%Y-%m"),
                "label": _get_persian_month(month),
                "revenue": float(revenue),
                "orders": orders_count,
            })

        return months_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"خطا در نمودار درآمد: {str(e)}"
        )


# ============ پرفروش‌ترین محصولات ============
@router.get("/reports/top-products")
def get_top_products(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """پرفروش‌ترین محصولات."""
    try:
        results = (
            db.query(
                OrderItem.product_id,
                func.sum(OrderItem.quantity).label("total_sold"),
                func.sum(OrderItem.price * OrderItem.quantity).label(
                    "total_revenue"
                ),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .filter(Order.status != OrderStatus.CANCELLED)
            .group_by(OrderItem.product_id)
            .order_by(desc("total_sold"))
            .limit(limit)
            .all()
        )

        products_data = []
        for product_id, sold, revenue in results:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                products_data.append({
                    "id": product.id,
                    "title": product.title,
                    "icon": product.icon,
                    "category": product.category,
                    "sold": int(sold or 0),
                    "revenue": float(revenue or 0),
                })

        return products_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"خطا در پرفروش‌ها: {str(e)}"
        )


# ============ بهترین مربیان ============
@router.get("/reports/top-trainers")
def get_top_trainers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """بهترین مربیان بر اساس تعداد برنامه."""
    try:
        trainers = db.query(User).filter(User.role == UserRole.TRAINER).all()

        trainers_data = []
        for trainer in trainers:
            plans_count = (
                db.query(func.count(TrainerPlan.id))
                .filter(TrainerPlan.trainer_id == trainer.id)
                .scalar()
                or 0
            )
            nutrition_count = (
                db.query(func.count(NutritionPlan.id))
                .filter(NutritionPlan.trainer_id == trainer.id)
                .scalar()
                or 0
            )

            trainers_data.append({
                "id": trainer.id,
                "name": trainer.full_name,
                "avatar": trainer.avatar or "👨‍🏫",
                "specialty": trainer.specialty or "مربی",
                "rating": trainer.rating or 0,
                "sessions_count": trainer.sessions_count or 0,
                "plans_count": plans_count,
                "nutrition_count": nutrition_count,
            })

        trainers_data.sort(
            key=lambda x: x["plans_count"] + x["nutrition_count"], reverse=True
        )
        return trainers_data[:5]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"خطا در بهترین مربیان: {str(e)}"
        )


# ============ آمار مشتریان ============
@router.get("/reports/customer-stats")
def get_customer_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """آمار مشتریان."""
    try:
        # پلن‌ها
        plan_distribution = {}
        for plan in ["bronze", "silver", "gold"]:
            count = (
                db.query(func.count(User.id))
                .filter(User.role == UserRole.CUSTOMER, User.plan == plan)
                .scalar()
                or 0
            )
            plan_distribution[plan] = count

        # وضعیت سفارش‌ها
        order_statuses = {}
        for status in OrderStatus:
            count = (
                db.query(func.count(Order.id))
                .filter(Order.status == status)
                .scalar()
                or 0
            )
            order_statuses[status.value] = count

        # کاربران فعال vs غیرفعال
        active_users = (
            db.query(func.count(User.id))
            .filter(User.is_active == True)
            .scalar()
            or 0
        )
        inactive_users = (
            db.query(func.count(User.id))
            .filter(User.is_active == False)
            .scalar()
            or 0
        )

        return {
            "plan_distribution": plan_distribution,
            "order_statuses": order_statuses,
            "active_users": active_users,
            "inactive_users": inactive_users,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"خطا در آمار مشتریان: {str(e)}"
        )


# ============ آخرین سفارش‌ها ============
@router.get("/orders")
def get_recent_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """آخرین سفارش‌ها."""
    try:
        orders = (
            db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
        )
        return [
            {
                "id": o.id,
                "user_id": o.user_id,
                "total": o.total,
                "status": o.status.value if o.status else "pending",
                "created_at": o.created_at.isoformat() if o.created_at else "",
            }
            for o in orders
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"خطا در سفارش‌ها: {str(e)}"
        )