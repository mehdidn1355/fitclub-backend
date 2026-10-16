from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LessonBase(BaseModel):
    title: str
    duration: str
    order: int = 1
    is_free: bool = False
    video_url: Optional[str] = None


class LessonResponse(LessonBase):
    id: int

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    title: str
    description: str
    category: str
    level: str
    price: float
    price_old: Optional[float] = None
    duration: str
    icon: str = "🎓"


class CourseCreate(CourseBase):
    is_new: bool = False
    is_bestseller: bool = False
    trainer_id: Optional[int] = None


class CourseResponse(CourseBase):
    id: int
    lessons_count: int
    rating: float
    students_count: int
    is_new: bool
    is_bestseller: bool
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CourseWithLessons(CourseResponse):
    lessons: List[LessonResponse] = []