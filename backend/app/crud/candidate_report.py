"""
CandidateReport DAO for database operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import BaseDAO
from app.models.candidate_report import CandidateReport
from app.schemas.candidate_report import CandidateReportResponse, CandidateReportCreate, CandidateReportUpdate


class CandidateReportDAO(BaseDAO[CandidateReport, CandidateReportResponse, CandidateReportCreate, CandidateReportUpdate]):
    """Data Access Object for CandidateReport operations."""

    def __init__(self):
        super().__init__(CandidateReport, CandidateReportResponse)

    def get(self, db: Session, id: int) -> Optional[CandidateReportResponse]:
        """Get a candidate report by ID."""
        report = db.query(self.model).filter(self.model.id == id).first()
        return CandidateReportResponse.from_model(report) if report else None

    def get_by_candidate_id(self, db: Session, candidate_id: int) -> Optional[CandidateReportResponse]:
        """Get a candidate report by candidate ID."""
        report = db.query(self.model).filter(self.model.candidate_id == candidate_id).first()
        return CandidateReportResponse.from_model(report) if report else None

    def create(self, db: Session, *, obj_in: CandidateReportCreate, created_by_user_id: int | None = None) -> CandidateReportResponse:
        """Create a new candidate report."""
        report = obj_in.to_model()
        db.add(report)
        db.commit()
        db.refresh(report)
        return CandidateReportResponse.from_model(report)

    def update(self, db: Session, *, db_obj: CandidateReport, obj_in: CandidateReportUpdate) -> CandidateReportResponse:
        """Update an existing candidate report."""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Handle risk_factors conversion
        if "risk_factors" in update_data and update_data["risk_factors"] is not None:
            update_data["risk_factors"] = [rf.model_dump() for rf in update_data["risk_factors"]]
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return CandidateReportResponse.from_model(db_obj)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a candidate report by ID."""
        report = db.query(self.model).filter(self.model.id == id).first()
        if report:
            db.delete(report)
            db.commit()
            return True
        return False

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        """Get multiple candidate reports with pagination."""
        reports = db.query(self.model).offset(skip).limit(limit).all()
        return [CandidateReportResponse.from_model(report) for report in reports]

    def create_or_update_by_candidate_id(
        self, 
        db: Session, 
        candidate_id: int, 
        report_data: CandidateReportCreate
    ) -> CandidateReportResponse:
        """
        Create a new report or update existing report for a candidate.
        Since each candidate should have only one report, this method handles both cases.
        """
        existing_report = db.query(self.model).filter(self.model.candidate_id == candidate_id).first()
        
        if existing_report:
            # Update existing report
            update_data = CandidateReportUpdate(
                header=report_data.header,
                risk_factors=report_data.risk_factors,
                overall_risk_level=report_data.overall_risk_level,
                general_observation=report_data.general_observation,
                final_grade=report_data.final_grade,
                general_impression=report_data.general_impression,
                confidence_score=report_data.confidence_score,
                key_strengths=report_data.key_strengths,
                areas_of_concern=report_data.areas_of_concern
            )
            return self.update(db, db_obj=existing_report, obj_in=update_data)
        else:
            # Create new report
            return self.create(db, obj_in=report_data)
