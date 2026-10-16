from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.course import Course, Lesson
from app.models.user import User
from app.schemas.course import (
    CourseResponse,
    CourseWithLessons,
    CourseCreate,
    LessonResponse,
)
from app.auth.dependencies import require_trainer

router = APIRouter(prefix="/api/courses", tags=["Courses"])


class VideoUpdate(BaseModel):
    video_url: Optional[str] = None


@router.get("", response_model=List[CourseResponse])
def list_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """لیست همه‌ی دوره‌ها با فیلتر."""
    query = db.query(Course).filter(Course.is_published == True)

    if category and category != "همه":
        query = query.filter(Course.category == category)
    if level and level != "همه":
        query = query.filter(Course.level == level)
    if search:
        query = query.filter(Course.title.contains(search))

    return query.order_by(Course.id).all()


@router.get("/{course_id}", response_model=CourseWithLessons)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """جزئیات یک دوره."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="دوره یافت نشد")
    return course


@router.get("/{course_id}/lessons", response_model=List[LessonResponse])
def get_lessons(course_id: int, db: Session = Depends(get_db)):
    """لیست درس‌های یک دوره."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="دوره یافت نشد")
    return (
        db.query(Lesson)
        .filter(Lesson.course_id == course_id)
        .order_by(Lesson.order)
        .all()
    )


@router.post("", response_model=CourseResponse, status_code=201)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    """ساخت دوره‌ی جدید (فقط مربی/ادمین)."""
    course = Course(
        **course_data.model_dump(),
        trainer_id=current_user.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.put("/lessons/{lesson_id}/video", response_model=LessonResponse)
def update_lesson_video(
    lesson_id: int,
    data: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer),
):
    """آپدیت ویدئوی یک درس (فقط مربی)."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson.video_url = data.video_url
    db.commit()
    db.refresh(lesson)
    return lesson