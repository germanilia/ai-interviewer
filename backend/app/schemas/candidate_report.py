from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from enum import StrEnum

if TYPE_CHECKING:
    from app.models.candidate_report import CandidateReport


class ReportGrade(StrEnum):
    """Report final grade enum"""
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    POOR = "poor"
    FAIL = "fail"


class RiskLevel(StrEnum):
    """Risk level enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskFactor(BaseModel):
    """Individual risk factor schema"""
    category: str = Field(..., description="Risk category (e.g., 'Criminal Background', 'Ethics')")
    description: str = Field(..., description="Description of the risk factor")
    severity: RiskLevel = Field(..., description="Severity level of this risk factor")
    evidence: Optional[str] = Field(None, description="Evidence or quotes supporting this risk factor")


class CandidateReportBase(BaseModel):
    """Base candidate report schema with common fields."""
    # Header information
    header: str = Field(..., description="Report header/title")
    
    # Risk assessment
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="List of identified risk factors")
    overall_risk_level: RiskLevel = Field(..., description="Overall risk assessment")
    
    # General observations
    general_observation: str = Field(..., description="General observations about the candidate")
    
    # Final assessment
    final_grade: ReportGrade = Field(..., description="Final grade for the candidate")
    general_impression: str = Field(..., description="General impression and recommendation")
    
    # Additional metadata
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in the assessment (0-1)")
    key_strengths: Optional[List[str]] = Field(default_factory=list, description="Key strengths identified")
    areas_of_concern: Optional[List[str]] = Field(default_factory=list, description="Areas requiring attention")


class CandidateReportCreate(CandidateReportBase):
    """Schema for creating a new candidate report."""
    candidate_id: int = Field(..., description="ID of the candidate this report belongs to")

    def to_model(self) -> "CandidateReport":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.candidate_report import CandidateReport
        return CandidateReport(
            candidate_id=self.candidate_id,
            header=self.header,
            risk_factors=[rf.model_dump() for rf in self.risk_factors],
            overall_risk_level=self.overall_risk_level,
            general_observation=self.general_observation,
            final_grade=self.final_grade,
            general_impression=self.general_impression,
            confidence_score=self.confidence_score,
            key_strengths=self.key_strengths or [],
            areas_of_concern=self.areas_of_concern or []
        )


class CandidateReportUpdate(BaseModel):
    """Schema for updating a candidate report."""
    header: Optional[str] = None
    risk_factors: Optional[List[RiskFactor]] = None
    overall_risk_level: Optional[RiskLevel] = None
    general_observation: Optional[str] = None
    final_grade: Optional[ReportGrade] = None
    general_impression: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    key_strengths: Optional[List[str]] = None
    areas_of_concern: Optional[List[str]] = None


class CandidateReportResponse(CandidateReportBase):
    """Schema for candidate report responses."""
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, report: "CandidateReport") -> "CandidateReportResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        # Convert risk_factors from JSON to RiskFactor objects
        risk_factors = []
        if report.risk_factors:
            for rf_data in report.risk_factors:
                risk_factors.append(RiskFactor(**rf_data))
        
        return cls(
            id=report.id,
            candidate_id=report.candidate_id,
            header=report.header,
            risk_factors=risk_factors,
            overall_risk_level=report.overall_risk_level,
            general_observation=report.general_observation,
            final_grade=report.final_grade,
            general_impression=report.general_impression,
            confidence_score=report.confidence_score,
            key_strengths=report.key_strengths or [],
            areas_of_concern=report.areas_of_concern or [],
            created_at=report.created_at,
            updated_at=report.updated_at
        )


class CandidateReportInDB(CandidateReportResponse):
    """Schema for candidate report data as stored in database."""

    @classmethod
    def from_model(cls, report: "CandidateReport") -> "CandidateReportInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(report)
