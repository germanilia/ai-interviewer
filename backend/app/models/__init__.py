# backend/app/models/__init__.py

from app.db import Base
from .user import User
from .candidate import Candidate
from .interview import Interview, Question, InterviewQuestion
from .interview_session import InterviewSession
from .candidate_report import CandidateReport

__all__ = ["User", "Candidate", "Interview", "Question", "InterviewQuestion", "InterviewSession", "CandidateReport", "Base"]  # Export your models for easier access