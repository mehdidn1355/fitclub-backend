from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseResponse

router = APIRouter(prefix="/api/exercises", tags=["Exercises"])


BODY_PARTS = [
    "سینه",
    "پشت",
    "پا",
    "سرشانه",
    "بازو",
    "شکم",
    "کاردیو",
]


@router.get("/body-parts", response_model=List[str])
def get_body_parts():
    """لیست نواحی بدن برای انتخاب در Wizard."""
    return BODY_PARTS


@router.get("", response_model=List[ExerciseResponse])
def list_exercises(
    muscle_group: Optional[str] = None,
    body_parts: Optional[str] = None,
    difficulty: Optional[str] = None,
    equipment_needed: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """لیست حرکات با فیلتر."""
    query = db.query(Exercise)

    if muscle_group and muscle_group != "همه":
        query = query.filter(Exercise.muscle_group == muscle_group)

    # فیلتر چند ناحیه‌ای ("سینه,بازو")
    if body_parts:
        parts = [p.strip() for p in body_parts.split(",")]
        query = query.filter(Exercise.muscle_group.in_(parts))

    if difficulty and difficulty != "همه":
        query = query.filter(Exercise.difficulty == difficulty)

    if equipment_needed:
        query = query.filter(Exercise.equipment_needed == equipment_needed)

    return query.order_by(Exercise.id).all()


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """جزئیات یک حرکت."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise