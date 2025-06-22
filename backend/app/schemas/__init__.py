# backend/app/schemas/__init__.py

from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB
from .candidate import CandidateBase, CandidateCreate, CandidateUpdate, CandidateResponse, CandidateWithInterviews, CandidateInDB
from .interview import InterviewBase, InterviewCreate, InterviewUpdate, InterviewResponse, InterviewWithCandidate, InterviewWithJob, InterviewWithDetails, InterviewWithQuestions, InterviewInDB, InterviewReport
from .question import QuestionBase, QuestionCreate, QuestionUpdate, QuestionResponse, QuestionWithCreator, QuestionInDB
from .job import JobBase, JobCreate, JobUpdate, JobResponse, JobWithCreator, JobWithQuestions, JobInDB
from .job_question import JobQuestionBase, JobQuestionCreate, JobQuestionUpdate, JobQuestionResponse, JobQuestionWithDetails, JobQuestionInDB
from .interview_question import InterviewQuestionBase, InterviewQuestionCreate, InterviewQuestionUpdate, InterviewQuestionResponse, InterviewQuestionWithDetails, InterviewQuestionInDB
from .auth import SignUpRequest, SignUpResponse, ConfirmSignUpRequest, ConfirmSignUpResponse, SignInRequest, SignInResponse, RefreshTokenRequest, RefreshTokenResponse, UserInfo, TokenData, PasswordChangeRequest, PasswordResetRequest

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    # Candidate schemas
    "CandidateBase", "CandidateCreate", "CandidateUpdate", "CandidateResponse", "CandidateWithInterviews", "CandidateInDB",
    # Interview schemas
    "InterviewBase", "InterviewCreate", "InterviewUpdate", "InterviewResponse", "InterviewWithCandidate", "InterviewWithJob", "InterviewWithDetails", "InterviewWithQuestions", "InterviewInDB", "InterviewReport",
    # Question schemas
    "QuestionBase", "QuestionCreate", "QuestionUpdate", "QuestionResponse", "QuestionWithCreator", "QuestionInDB",
    # Job schemas
    "JobBase", "JobCreate", "JobUpdate", "JobResponse", "JobWithCreator", "JobWithQuestions", "JobInDB",
    # Job Question schemas
    "JobQuestionBase", "JobQuestionCreate", "JobQuestionUpdate", "JobQuestionResponse", "JobQuestionWithDetails", "JobQuestionInDB",
    # Interview Question schemas
    "InterviewQuestionBase", "InterviewQuestionCreate", "InterviewQuestionUpdate", "InterviewQuestionResponse", "InterviewQuestionWithDetails", "InterviewQuestionInDB",
    # Auth schemas
    "SignUpRequest", "SignUpResponse", "ConfirmSignUpRequest", "ConfirmSignUpResponse", "SignInRequest", "SignInResponse", "RefreshTokenRequest", "RefreshTokenResponse", "UserInfo", "TokenData", "PasswordChangeRequest", "PasswordResetRequest"
]