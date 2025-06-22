# backend/app/schemas/__init__.py

from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB
from .candidate import CandidateBase, CandidateCreate, CandidateUpdate, CandidateResponse, CandidateInDB
from .interview import InterviewBase, InterviewCreate, InterviewUpdate, InterviewResponse, InterviewInDB, InterviewReport
from .question import QuestionBase, QuestionCreate, QuestionUpdate, QuestionResponse, QuestionInDB
from .job import JobBase, JobCreate, JobUpdate, JobResponse, JobWithQuestions, JobInDB
from .job_question import JobQuestionBase, JobQuestionCreate, JobQuestionUpdate, JobQuestionResponse, JobQuestionInDB
from .interview_question import InterviewQuestionBase, InterviewQuestionCreate, InterviewQuestionUpdate, InterviewQuestionResponse, InterviewQuestionInDB
from .auth import SignUpRequest, SignUpResponse, ConfirmSignUpRequest, ConfirmSignUpResponse, SignInRequest, SignInResponse, RefreshTokenRequest, RefreshTokenResponse, UserInfo, TokenData, PasswordChangeRequest, PasswordResetRequest

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    # Candidate schemas
    "CandidateBase", "CandidateCreate", "CandidateUpdate", "CandidateResponse", "CandidateInDB",
    # Interview schemas
    "InterviewBase", "InterviewCreate", "InterviewUpdate", "InterviewResponse", "InterviewInDB", "InterviewReport",
    # Question schemas
    "QuestionBase", "QuestionCreate", "QuestionUpdate", "QuestionResponse", "QuestionInDB",
    # Job schemas
    "JobBase", "JobCreate", "JobUpdate", "JobResponse", "JobWithQuestions", "JobInDB",
    # Job Question schemas
    "JobQuestionBase", "JobQuestionCreate", "JobQuestionUpdate", "JobQuestionResponse", "JobQuestionInDB",
    # Interview Question schemas
    "InterviewQuestionBase", "InterviewQuestionCreate", "InterviewQuestionUpdate", "InterviewQuestionResponse", "InterviewQuestionInDB",
    # Auth schemas
    "SignUpRequest", "SignUpResponse", "ConfirmSignUpRequest", "ConfirmSignUpResponse", "SignInRequest", "SignInResponse", "RefreshTokenRequest", "RefreshTokenResponse", "UserInfo", "TokenData", "PasswordChangeRequest", "PasswordResetRequest"
]