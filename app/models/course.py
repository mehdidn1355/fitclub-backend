from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    level = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    price_old = Column(Float, nullable=True)
    duration = Column(String, nullable=False)
    lessons_count = Column(Integer, default=0)
    rating = Column(Float, default=0)
    students_count = Column(Integer, default=0)
    icon = Column(String, default="🎓")
    is_new = Column(Boolean, default=False)
    is_bestseller = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    order = Column(Integer, default=1)
    is_free = Column(Boolean, default=False)
    video_url = Column(String, nullable=True)

    course = relationship("Course", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress = Column(Integer, default=0)
    completed_lessons = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    course = relationship("Course", back_populates="enrollments")