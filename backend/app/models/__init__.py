# backend/app/models/__init__.py

from app.db import Base
from .user import User
from .candidate import Candidate
from .interview import Interview, Question, InterviewQuestion
from .interview_session import InterviewSession
from .candidate_report import CandidateReport
from .custom_prompt import CustomPrompt, PromptType

__all__ = ["User", "Candidate", "Interview", "Question", "InterviewQuestion", "InterviewSession", "CandidateReport", "CustomPrompt", "PromptType", "Base"]  # Export your models for easier access