# backend/app/models/__init__.py

from app.db import Base
from .user import User
from .candidate import Candidate
from .interview import Interview, Question, Job, JobQuestion, InterviewQuestion

__all__ = ["User", "Candidate", "Interview", "Question", "Job", "JobQuestion", "InterviewQuestion", "Base"]  # Export your models for easier access