"""
Two tables:
  - User: account + coaching state (skill_level, streak, daily question pref)
  - Submission: one row per code review, used to recompute streak/skill_level
                and to power a history view later.

Design note: username lives ONLY on User, and every other table (this one,
and any future Leaderboard/BattleMatch/Friendship table) references the
user by user_id foreign key and JOINs to read the username. That means a
username change via /api/user/update-username automatically shows up
everywhere else, with no denormalized copies to keep in sync.
"""
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # "beginner" learners get Hello-World-style questions; see services/llm.py
    skill_level = Column(String, default="beginner", nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    last_practice_date = Column(Date, nullable=True)

    # Requirement: default is 1, not 3. Options exposed in the UI: 1 / 3 / 5.
    daily_question_count = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    submissions = relationship(
        "Submission", back_populates="user", cascade="all, delete-orphan"
    )


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    language = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    question_title = Column(String, nullable=False)

    code = Column(Text, nullable=False)
    review_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="submissions")
