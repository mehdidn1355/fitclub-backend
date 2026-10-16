from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0.0
    items_to_create = []

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {item.product_id} not found"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, detail=f"Not enough stock for {product.title}"
            )

        total += product.price * item.quantity
        items_to_create.append({
            "product_id": product.id,
            "title": product.title,
            "price": product.price,
            "quantity": item.quantity,
        })

    order = Order(
        user_id=current_user.id,
        total=total,
        shipping_name=order_data.shipping_name,
        shipping_phone=order_data.shipping_phone,
        shipping_address=order_data.shipping_address,
        shipping_postal_code=order_data.shipping_postal_code,
        payment_method=order_data.payment_method,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.flush()

    for item_data in items_to_create:
        db.add(OrderItem(order_id=order.id, **item_data))
        product = (
            db.query(Product)
            .filter(Product.id == item_data["product_id"])
            .first()
        )
        product.stock -= item_data["quantity"]

    db.commit()
    db.refresh(order)
    return order


@router.get("/my", response_model=List[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("", response_model=List[OrderResponse])
def all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return {"message": "Order status updated", "status": status.value}