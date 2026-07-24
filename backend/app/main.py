from datetime import date
from typing import Optional, Any, List
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.routers.auth import router as auth_router
from app.services.llm import generate_question, review_code_ai

# Initialize FastAPI App
app = FastAPI(title="CodeCoach MVP API")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("\n================ 🚨 422 VALIDATION ERROR 🚨 ================")
    print(f"Validation Errors: {exc.errors()}")
    print("===========================================================\n")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


# Updated origins to allow local dev + Vercel frontend domains
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://codecoach-mvp-bb6l.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to "*" so any Vercel preview/production link can access the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root & Health Check Endpoints (Fixes 404s in Render logs)
@app.get("/")
async def root():
    return {"message": "CodeCoach MVP API is live and running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(auth_router)

# In-memory user state database for streaks & skill progression
USER_PROGRESS = {}


def get_user_state(user_id: str) -> dict:
    if user_id not in USER_PROGRESS:
        USER_PROGRESS[user_id] = {
            "streak": 0,
            "last_date": None,
            "total_solved": 0,
            "total_attempts": 0,
            "skill_level": "beginner",
            "is_new_user": True,
        }
    return USER_PROGRESS[user_id]


def update_user_skill_level(user_data: dict) -> str:
    """Adaptive Algorithm: Upgrades user level based on total correct solves."""
    total_solved = user_data["total_solved"]

    if total_solved >= 10:
        new_level = "advanced"
    elif total_solved >= 4:
        new_level = "intermediate"
    else:
        new_level = "beginner"

    user_data["skill_level"] = new_level
    return new_level


def record_submission_and_streak(user_id: str, passed: bool) -> tuple[int, str]:
    today = date.today()
    data = get_user_state(user_id)
    data["total_attempts"] += 1
    data["is_new_user"] = False

    if passed:
        data["total_solved"] += 1

        # Calculate daily streak
        last_date = data["last_date"]
        if last_date == today:
            pass
        elif last_date and last_date == date.fromordinal(today.toordinal() - 1):
            data["streak"] += 1
        else:
            data["streak"] = 1

        data["last_date"] = today

    current_level = update_user_skill_level(data)
    return data["streak"], current_level


class QuestionRequest(BaseModel):
    user_id: Optional[str] = "default_user"
    skill_level: Optional[str] = None
    language: str = Field(default="python")
    topic_history: Optional[List[str]] = Field(default_factory=list)
    count: int = Field(default=1, ge=1, le=10)


class QuestionResponse(BaseModel):
    title: str
    topic: str
    difficulty: str
    prompt: str
    example_input: str
    example_output: str
    constraints: str


@app.post("/api/generate-question", response_model=List[QuestionResponse])
async def generate_question_endpoint(request: QuestionRequest):
    try:
        user_data = get_user_state(request.user_id or "default_user")
        
        effective_level = request.skill_level or user_data["skill_level"]
        is_new = user_data["is_new_user"]

        return await generate_question(
            skill_level=effective_level,
            language=request.language,
            topic_history=request.topic_history or [],
            count=request.count,
            is_new_user=is_new,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}",
        )


class CodeReviewRequest(BaseModel):
    user_id: Optional[str] = "default_user"
    code: Optional[Any] = Field(default="", alias="user_code")
    language: Optional[str] = "python"
    question_prompt: Optional[Any] = Field(default="", alias="question")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("question_prompt", mode="before")
    def parse_question_prompt(cls, v):
        if isinstance(v, dict):
            return v.get("prompt") or v.get("title") or str(v)
        return str(v) if v is not None else ""

    @field_validator("code", mode="before")
    def parse_code(cls, v):
        return str(v) if v is not None else ""


class CodeReviewResponse(BaseModel):
    status: str
    feedback: str
    passed: bool
    current_streak: int
    user_skill_level: str


@app.post("/api/review-code", response_model=CodeReviewResponse)
async def review_code_endpoint(request: CodeReviewRequest):
    try:
        uid_str = request.user_id or "default_user"
        prompt_str = request.question_prompt or "Evaluate user code."
        code_str = request.code or ""
        lang_str = request.language or "python"

        ai_result = await review_code_ai(
            question_prompt=prompt_str,
            language=lang_str,
            user_code=code_str,
        )

        passed = ai_result.get("passed", False)
        updated_streak, updated_level = record_submission_and_streak(uid_str, passed)

        return CodeReviewResponse(
            status=ai_result.get("status", "failed"),
            feedback=ai_result.get("feedback", "Unable to generate review feedback."),
            passed=passed,
            current_streak=updated_streak,
            user_skill_level=updated_level,
        )
    except Exception as e:
        print(f"Error during AI review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to review code: {str(e)}",
        )