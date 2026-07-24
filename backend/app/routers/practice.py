"""
Practice routes: question generation and streaming code review.

review-code streams the AI's response straight through to the client as
it's generated (word-by-word), then — once the stream is exhausted —
persists a Submission row and updates the user's streak/skill_level.
That update has to happen after the generator is fully consumed, so it's
wired in as a wrapper generator rather than a separate post-stream step.
"""
from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..db import models
from ..db.database import get_db
from ..services import llm

router = APIRouter(prefix="/api", tags=["practice"])

BEGINNER_GRADUATION_THRESHOLD = 7  # solved beginner submissions before leveling up


# ---------- request / response schemas ----------

class GenerateQuestionRequest(BaseModel):
    language: str


class QuestionSchema(BaseModel):
    title: str
    topic: str
    difficulty: str
    prompt: str
    example_input: str | None = ""
    example_output: str | None = ""
    constraints: str | None = ""


class ReviewCodeRequest(BaseModel):
    question: QuestionSchema
    language: str
    code: str


# ---------- routes ----------

@router.post("/generate-question")
async def generate_question(
    payload: GenerateQuestionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recent = (
        db.query(models.Submission)
        .filter(
            models.Submission.user_id == current_user.id,
            models.Submission.language == payload.language,
        )
        .order_by(models.Submission.created_at.desc())
        .limit(6)
        .all()
    )
    topic_history = [s.topic for s in recent]

    question = await llm.generate_question(
        skill_level=current_user.skill_level,
        language=payload.language,
        topic_history=topic_history,
    )
    return question


def _update_streak_and_skill(db: Session, user: models.User, difficulty: str) -> None:
    """Runs once per submission, after the review stream finishes."""
    today = date.today()
    if user.last_practice_date != today:
        if user.last_practice_date == date.fromordinal(today.toordinal() - 1):
            user.streak += 1
        else:
            user.streak = 1
        user.last_practice_date = today

    if user.skill_level == "beginner" and difficulty == "beginner":
        beginner_solved = (
            db.query(models.Submission)
            .filter(
                models.Submission.user_id == user.id,
                models.Submission.difficulty == "beginner",
            )
            .count()
        )
        if beginner_solved + 1 >= BEGINNER_GRADUATION_THRESHOLD:
            user.skill_level = "easy"

    db.add(user)
    db.commit()


@router.post("/review-code")
async def review_code(
    payload: ReviewCodeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    async def event_stream():
        full_text_parts: list[str] = []
        async for chunk in llm.stream_code_review(
            payload.question.dict(), payload.language, payload.code
        ):
            full_text_parts.append(chunk)
            yield chunk

        # Persist after the client has received the full stream.
        submission = models.Submission(
            user_id=current_user.id,
            language=payload.language,
            topic=payload.question.topic,
            difficulty=payload.question.difficulty,
            question_title=payload.question.title,
            code=payload.code,
            review_text="".join(full_text_parts),
        )
        db.add(submission)
        _update_streak_and_skill(db, current_user, payload.question.difficulty)

    return StreamingResponse(event_stream(), media_type="text/plain")
