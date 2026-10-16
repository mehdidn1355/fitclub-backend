"""
اسکریپت ساخت سفارش‌های نمونه برای پر کردن گزارش‌ها.
اجرا: python seed_orders.py
"""
import random
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus


def seed_orders():
    db = SessionLocal()

    try:
        # کاربران عادی
        customers = db.query(User).filter(User.role == UserRole.CUSTOMER).all()
        if not customers:
            print("❌ هیچ کاربر عادی وجود نداره. اول seed.py رو اجرا کن.")
            return

        # محصولات
        products = db.query(Product).all()
        if not products:
            print("❌ هیچ محصولی وجود نداره. اول seed.py رو اجرا کن.")
            return

        # پاک کردن سفارش‌های قبلی
        print("پاک کردن سفارش‌های قبلی...")
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.commit()

        # وضعیت‌ها با وزن
        statuses = [
            (OrderStatus.DELIVERED, 60),  # ۶۰٪ تحویل شده
            (OrderStatus.SHIPPED, 15),    # ۱۵٪ ارسال شده
            (OrderStatus.PENDING, 20),    # ۲۰٪ در انتظار
            (OrderStatus.CANCELLED, 5),   # ۵٪ لغو شده
        ]

        status_list = []
        for status, weight in statuses:
            status_list.extend([status] * weight)

        # ساخت ۵۰ سفارش در ۶ ماه اخیر
        orders_count = 50
        print(f"ساخت {orders_count} سفارش در ۶ ماه اخیر...")

        for i in range(orders_count):
            # تاریخ تصادفی در ۶ ماه اخیر
            days_ago = random.randint(0, 180)
            created_at = datetime.now() - timedelta(days=days_ago)

            # مشتری تصادفی
            customer = random.choice(customers)

            # ۱ تا ۳ محصول تصادفی
            items = random.sample(products, random.randint(1, 3))
            total = 0
            order_items = []

            for product in items:
                qty = random.randint(1, 3)
                price = product.price
                total += price * qty
                order_items.append({
                    "product_id": product.id,
                    "title": product.title,
                    "price": price,
                    "quantity": qty,
                })

            # وضعیت تصادفی
            status = random.choice(status_list)

            # ساخت سفارش
            order = Order(
                user_id=customer.id,
                total=total,
                status=status,
                payment_method=random.choice(["online", "cod"]),
                shipping_name=customer.full_name,
                shipping_phone="09123456789",
                shipping_address="تهران، خیابان ولیعصر",
                shipping_postal_code="1234567890",
                created_at=created_at,
            )
            db.add(order)
            db.flush()

            for item in order_items:
                db.add(OrderItem(order_id=order.id, **item))

        db.commit()
        print(f"✓ {orders_count} سفارش ساخته شد")

        # آمار
        total_orders = db.query(Order).count()
        total_revenue = sum(o.total for o in db.query(Order).filter(
            Order.status != OrderStatus.CANCELLED
        ).all())

        print("")
        print("=" * 50)
        print("✅ سفارش‌های نمونه ساخته شدند!")
        print("=" * 50)
        print(f"📦 تعداد سفارش‌ها: {total_orders}")
        print(f"💰 کل درآمد: {total_revenue:,.0f} تومان")
        print("")

    except Exception as e:
        print(f"❌ خطا: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_orders()