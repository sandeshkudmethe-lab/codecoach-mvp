"""
Account routes: register, login, and the two profile endpoints from the
spec (/api/user/profile, /api/user/update-username). Kept in this file
rather than a separate users.py to match the given folder structure —
these are all "who is this account" concerns.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..db import models
from ..db.database import get_db

router = APIRouter(prefix="/api", tags=["auth"])


# ---------- request / response schemas ----------

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    skill_level: str
    streak: int
    daily_question_count: int

    class Config:
        from_attributes = True


class UpdateUsernameRequest(BaseModel):
    username: str


# ---------- routes ----------

@router.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User)
        .filter(
            (models.User.username == payload.username)
            | (models.User.email == payload.email)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already taken")

    user = models.User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        skill_level="beginner",
        streak=0,
        daily_question_count=1,  # requirement: default is 1, not 3
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token)


@router.get("/user/profile", response_model=UserOut)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/user/update-username", response_model=UserOut)
def update_username(
    payload: UpdateUsernameRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_username = payload.username.strip()
    if not new_username:
        raise HTTPException(status_code=400, detail="Username can't be empty")

    if new_username != current_user.username:
        clash = db.query(models.User).filter(models.User.username == new_username).first()
        if clash:
            raise HTTPException(status_code=400, detail="That username is already taken")

        # Single point of truth: every other table references user_id and
        # JOINs back to this row, so this one write is all that's needed —
        # leaderboard / battle mode / friends list (once built) read this
        # live rather than storing their own copy of the username.
        current_user.username = new_username
        db.commit()
        db.refresh(current_user)

    return current_user
