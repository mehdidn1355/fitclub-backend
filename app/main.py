from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import (
    auth,
    users,
    courses,
    products,
    orders,
    admin,
    exercises,
    plans,
    nutrition,
    upload,
    chat,
)

# ساخت جداول دیتابیس (اگه وجود نداشته باشن)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API پلتفرم FitClub 🏋️",
)

# CORS — اجازه‌ی ارتباط Frontend با Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# اتصال router ها
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(exercises.router)
app.include_router(plans.router)
app.include_router(nutrition.router)
app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {
        "message": f"به {settings.APP_NAME} خوش آمدید 🏋️",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}