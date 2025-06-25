# backend/app/schemas/__init__.py

from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB
from .candidate import CandidateBase, CandidateCreate, CandidateUpdate, CandidateResponse, CandidateInDB
from .interview import InterviewBase, InterviewCreate, InterviewUpdate, InterviewResponse, InterviewInDB, InterviewReport
from .question import QuestionBase, QuestionCreate, QuestionUpdate, QuestionResponse, QuestionInDB
from .interview_question import InterviewQuestionBase, InterviewQuestionCreate, InterviewQuestionUpdate, InterviewQuestionResponse, InterviewQuestionInDB
from .auth import SignUpRequest, SignUpResponse, ConfirmSignUpRequest, ConfirmSignUpResponse, SignInRequest, SignInResponse, RefreshTokenRequest, RefreshTokenResponse, UserInfo, TokenData, PasswordChangeRequest, PasswordResetRequest
from .interview import InterviewListResponse, InterviewWithDetails
from .reports import (
    ReportFormat, ReportType, ChartType, ReportFrequency,
    ChartDataPoint, ChartData, SummaryCard, AnalyticsFilters,
    OverviewData, AnalyticsData, ReportGenerationRequest, ReportMetadata,
    CustomReportField, CustomReportDefinition, CustomReportRequest,
    ScheduledReportRequest, ScheduledReport, ReportHistoryItem,
    ReportExportRequest, ReportResponse, AnalyticsResponse,
    ReportListResponse, AvailableFieldsResponse
)

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    # Candidate schemas
    "CandidateBase", "CandidateCreate", "CandidateUpdate", "CandidateResponse", "CandidateInDB",
    # Interview schemas
    "InterviewBase", "InterviewCreate", "InterviewUpdate", "InterviewResponse", "InterviewInDB", "InterviewReport",
    # Question schemas
    "QuestionBase", "QuestionCreate", "QuestionUpdate", "QuestionResponse", "QuestionInDB",
    # Interview Question schemas
    "InterviewQuestionBase", "InterviewQuestionCreate", "InterviewQuestionUpdate", "InterviewQuestionResponse", "InterviewQuestionInDB",
    # Auth schemas
    "SignUpRequest", "SignUpResponse", "ConfirmSignUpRequest", "ConfirmSignUpResponse", "SignInRequest", "SignInResponse", "RefreshTokenRequest", "RefreshTokenResponse", "UserInfo", "TokenData", "PasswordChangeRequest", "PasswordResetRequest",
    # Common schemas
    "InterviewListResponse", "InterviewWithDetails",
    # Reports schemas
    "ReportFormat", "ReportType", "ChartType", "ReportFrequency",
    "ChartDataPoint", "ChartData", "SummaryCard", "AnalyticsFilters",
    "OverviewData", "AnalyticsData", "ReportGenerationRequest", "ReportMetadata",
    "CustomReportField", "CustomReportDefinition", "CustomReportRequest",
    "ScheduledReportRequest", "ScheduledReport", "ReportHistoryItem",
    "ReportExportRequest", "ReportResponse", "AnalyticsResponse",
    "ReportListResponse", "AvailableFieldsResponse"
]