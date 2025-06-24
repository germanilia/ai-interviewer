import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.crud.interview import InterviewDAO
from app.crud.candidate import CandidateDAO
from app.crud.job import JobDAO
from app.crud.reports import ReportsDAO
from app.schemas.reports import (
    OverviewData, AnalyticsData, ChartData, ChartDataPoint, SummaryCard,
    AnalyticsFilters, ReportGenerationRequest, ReportMetadata, ReportResponse,
    CustomReportDefinition, CustomReportRequest, AvailableFieldsResponse,
    CustomReportField, ChartType, ReportFormat, ReportType
)
from app.core.logging_service import get_logger

logger = get_logger(__name__)


class ReportsService:
    """Service for handling reports and analytics functionality."""

    def __init__(
        self,
        interview_dao: InterviewDAO,
        candidate_dao: CandidateDAO,
        job_dao: JobDAO,
        reports_dao: ReportsDAO
    ):
        self.interview_dao = interview_dao
        self.candidate_dao = candidate_dao
        self.job_dao = job_dao
        self.reports_dao = reports_dao

    def get_overview_data(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> OverviewData:
        """Get overview dashboard data with summary cards and charts."""
        logger.info("Generating overview dashboard data")

        # Get summary statistics from DAO
        summary_stats = self.reports_dao.get_summary_statistics(db, filters)
        summary_cards = self._build_summary_cards(summary_stats)

        # Get chart data from DAO
        monthly_trends = self.reports_dao.get_monthly_trends(db, filters)
        trends_chart = self._build_trends_chart(monthly_trends)

        risk_distribution = self.reports_dao.get_risk_distribution(db, filters)
        risk_distribution_chart = self._build_risk_distribution_chart(risk_distribution)

        department_breakdown = self.reports_dao.get_department_breakdown(db, filters)
        department_breakdown_chart = self._build_department_breakdown_chart(department_breakdown)

        # Get recent interviews
        recent_interviews_data = self.reports_dao.get_recent_interviews(db, limit=5)
        recent_interviews = self._build_recent_interviews_list(recent_interviews_data)

        return OverviewData(
            summary_cards=summary_cards,
            trends_chart=trends_chart,
            risk_distribution_chart=risk_distribution_chart,
            department_breakdown_chart=department_breakdown_chart,
            recent_interviews=recent_interviews
        )

    def get_analytics_data(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> AnalyticsData:
        """Get analytics dashboard data with detailed charts."""
        logger.info("Generating analytics dashboard data")

        # Get chart data from DAO
        daily_volume = self.reports_dao.get_daily_volume(db, days=30, filters=filters)
        interview_volume_chart = self._build_interview_volume_chart(daily_volume)

        weekly_risk_trends = self.reports_dao.get_weekly_risk_trends(db, weeks=12, filters=filters)
        risk_trends_chart = self._build_risk_trends_chart(weekly_risk_trends)

        monthly_completion = self.reports_dao.get_monthly_completion_rates(db, months=6, filters=filters)
        completion_rates_chart = self._build_completion_rates_chart(monthly_completion)

        score_distribution = self.reports_dao.get_score_distribution(db, filters)
        score_distribution_chart = self._build_score_distribution_chart(score_distribution)

        dept_avg_scores = self.reports_dao.get_department_avg_scores(db, filters)
        department_comparison_chart = self._build_department_comparison_chart(dept_avg_scores)

        completion_time_dist = self.reports_dao.get_completion_time_distribution(db, filters)
        time_to_complete_chart = self._build_time_to_complete_chart(completion_time_dist)

        return AnalyticsData(
            interview_volume_chart=interview_volume_chart,
            risk_trends_chart=risk_trends_chart,
            completion_rates_chart=completion_rates_chart,
            score_distribution_chart=score_distribution_chart,
            department_comparison_chart=department_comparison_chart,
            time_to_complete_chart=time_to_complete_chart,
            filters_applied=filters
        )

    def generate_report(self, db: Session, request: ReportGenerationRequest) -> ReportResponse:
        """Generate a report based on the request."""
        logger.info(f"Generating {request.report_type} report in {request.format} format")

        try:
            # Generate report based on type
            if request.report_type == ReportType.CANDIDATE:
                return self._generate_candidate_report(db, request)
            elif request.report_type == ReportType.INTERVIEW:
                return self._generate_interview_report(db, request)
            elif request.report_type == ReportType.ANALYTICS:
                return self._generate_analytics_report(db, request)
            elif request.report_type == ReportType.CUSTOM:
                return self._generate_custom_report(db, request)
            else:
                raise ValueError(f"Unsupported report type: {request.report_type}")

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return ReportResponse(
                success=False,
                message=f"Failed to generate report: {str(e)}"
            )

    def get_available_fields(self, data_source: str) -> AvailableFieldsResponse:
        """Get available fields for custom report building."""
        logger.info(f"Getting available fields for data source: {data_source}")

        fields_map = {
            "interviews": [
                CustomReportField(field_name="id", display_name="Interview ID", field_type="number"),
                CustomReportField(field_name="status", display_name="Status", field_type="string"),
                CustomReportField(field_name="score", display_name="Score", field_type="number"),
                CustomReportField(field_name="integrity_score", display_name="Integrity Score", field_type="string"),
                CustomReportField(field_name="risk_level", display_name="Risk Level", field_type="string"),
                CustomReportField(field_name="interview_date", display_name="Interview Date", field_type="date"),
                CustomReportField(field_name="completed_at", display_name="Completed At", field_type="date"),
                CustomReportField(field_name="candidate_name", display_name="Candidate Name", field_type="string"),
                CustomReportField(field_name="job_title", display_name="Job Title", field_type="string"),
                CustomReportField(field_name="job_department", display_name="Department", field_type="string"),
            ],
            "candidates": [
                CustomReportField(field_name="id", display_name="Candidate ID", field_type="number"),
                CustomReportField(field_name="first_name", display_name="First Name", field_type="string"),
                CustomReportField(field_name="last_name", display_name="Last Name", field_type="string"),
                CustomReportField(field_name="email", display_name="Email", field_type="string"),
                CustomReportField(field_name="phone", display_name="Phone", field_type="string"),
                CustomReportField(field_name="created_at", display_name="Created At", field_type="date"),
            ],
            "jobs": [
                CustomReportField(field_name="id", display_name="Job ID", field_type="number"),
                CustomReportField(field_name="title", display_name="Job Title", field_type="string"),
                CustomReportField(field_name="department", display_name="Department", field_type="string"),
                CustomReportField(field_name="description", display_name="Description", field_type="string"),
                CustomReportField(field_name="created_at", display_name="Created At", field_type="date"),
            ]
        }

        fields = fields_map.get(data_source, [])
        return AvailableFieldsResponse(data_source=data_source, fields=fields)

    # Chart builder methods - convert DAO data to chart objects
    def _build_summary_cards(self, summary_stats: Dict[str, Any]) -> List[SummaryCard]:
        """Build summary cards from statistics."""
        return [
            SummaryCard(
                title="Total Interviews",
                value=summary_stats["total_interviews"],
                description="All interviews in the system"
            ),
            SummaryCard(
                title="Completion Rate",
                value=f"{summary_stats['completion_rate']:.1f}%",
                description="Percentage of completed interviews"
            ),
            SummaryCard(
                title="Average Risk Score",
                value=f"{summary_stats['avg_score']:.1f}",
                description="Average integrity score"
            ),
            SummaryCard(
                title="Flagged Candidates",
                value=summary_stats["flagged_candidates"],
                description="High or critical risk candidates"
            )
        ]

    def _build_trends_chart(self, monthly_data: List[Dict[str, Any]]) -> ChartData:
        """Build trends chart from monthly data."""
        data_points = [
            ChartDataPoint(
                label=item["month"].strftime("%Y-%m") if item["month"] else "Unknown",
                value=item["count"]
            )
            for item in monthly_data
        ]

        return ChartData(
            title="Interview Trends",
            chart_type=ChartType.LINE,
            data=data_points,
            x_axis_label="Month",
            y_axis_label="Number of Interviews"
        )

    def _build_risk_distribution_chart(self, risk_data: List[Dict[str, Any]]) -> ChartData:
        """Build risk distribution chart from risk data."""
        data_points = [
            ChartDataPoint(label=item["risk_level"], value=item["count"])
            for item in risk_data
        ]

        return ChartData(
            title="Risk Distribution",
            chart_type=ChartType.PIE,
            data=data_points
        )

    def _build_department_breakdown_chart(self, dept_data: List[Dict[str, Any]]) -> ChartData:
        """Build department breakdown chart from department data."""
        data_points = [
            ChartDataPoint(label=item["department"], value=item["count"])
            for item in dept_data
        ]

        return ChartData(
            title="Department Breakdown",
            chart_type=ChartType.BAR,
            data=data_points,
            x_axis_label="Department",
            y_axis_label="Number of Interviews"
        )

    def _build_recent_interviews_list(self, interviews_data: List) -> List[Dict[str, Any]]:
        """Build recent interviews list from interview data."""
        return [
            {
                "id": interview.id,
                "candidate_name": f"{interview.candidate.first_name} {interview.candidate.last_name}" if interview.candidate else "Unknown",
                "job_title": interview.job.title if interview.job else "Unknown",
                "status": interview.status.value if interview.status else "Unknown",
                "created_at": interview.created_at.isoformat() if interview.created_at else None
            }
            for interview in interviews_data
        ]

    def _build_interview_volume_chart(self, daily_data: List[Dict[str, Any]]) -> ChartData:
        """Build interview volume chart from daily data."""
        data_points = [
            ChartDataPoint(
                label=item["day"].strftime("%Y-%m-%d") if item["day"] else "Unknown",
                value=item["count"]
            )
            for item in daily_data
        ]

        return ChartData(
            title="Interview Volume (Last 30 Days)",
            chart_type=ChartType.LINE,
            data=data_points,
            x_axis_label="Date",
            y_axis_label="Number of Interviews"
        )

    def _build_risk_trends_chart(self, weekly_data: List[Dict[str, Any]]) -> ChartData:
        """Build risk trends chart from weekly data."""
        data_points = [
            ChartDataPoint(
                label=item["week"].strftime("%Y-W%U") if item["week"] else "Unknown",
                value=item["count"]
            )
            for item in weekly_data
        ]

        return ChartData(
            title="High Risk Trends (Last 12 Weeks)",
            chart_type=ChartType.LINE,
            data=data_points,
            x_axis_label="Week",
            y_axis_label="High Risk Interviews"
        )

    def _build_completion_rates_chart(self, monthly_data: List[Dict[str, Any]]) -> ChartData:
        """Build completion rates chart from monthly data."""
        data_points = [
            ChartDataPoint(
                label=item["month"].strftime("%Y-%m") if item["month"] else "Unknown",
                value=item["rate"]
            )
            for item in monthly_data
        ]

        return ChartData(
            title="Completion Rates (Last 6 Months)",
            chart_type=ChartType.BAR,
            data=data_points,
            x_axis_label="Month",
            y_axis_label="Completion Rate (%)"
        )

    def _build_score_distribution_chart(self, score_data: List[Dict[str, Any]]) -> ChartData:
        """Build score distribution chart from score data."""
        data_points = [
            ChartDataPoint(label=item["range"], value=item["count"])
            for item in score_data
        ]

        return ChartData(
            title="Score Distribution",
            chart_type=ChartType.BAR,
            data=data_points,
            x_axis_label="Score Range",
            y_axis_label="Number of Interviews"
        )

    def _build_department_comparison_chart(self, dept_data: List[Dict[str, Any]]) -> ChartData:
        """Build department comparison chart from department average score data."""
        data_points = [
            ChartDataPoint(label=item["department"], value=item["avg_score"])
            for item in dept_data
        ]

        return ChartData(
            title="Average Scores by Department",
            chart_type=ChartType.BAR,
            data=data_points,
            x_axis_label="Department",
            y_axis_label="Average Score"
        )

    def _build_time_to_complete_chart(self, time_data: List[Dict[str, Any]]) -> ChartData:
        """Build time to complete chart from completion time data."""
        data_points = [
            ChartDataPoint(label=item["range"], value=item["count"])
            for item in time_data
        ]

        return ChartData(
            title="Time to Complete Distribution",
            chart_type=ChartType.BAR,
            data=data_points,
            x_axis_label="Time Range",
            y_axis_label="Number of Interviews"
        )

    # Report generation methods
    def _generate_candidate_report(self, db: Session, request: ReportGenerationRequest) -> ReportResponse:
        """Generate candidate report."""
        if not request.candidate_id:
            return ReportResponse(success=False, message="Candidate ID is required for candidate reports")

        candidate = self.candidate_dao.get(db, request.candidate_id)
        if not candidate:
            return ReportResponse(success=False, message="Candidate not found")

        # Mock report generation - in real implementation, this would generate actual files
        report_id = 1  # This would be generated from database
        download_url = f"/api/v1/reports/download/{report_id}"

        metadata = ReportMetadata(
            id=report_id,
            title=f"Candidate Report - {candidate.first_name} {candidate.last_name}",
            report_type=ReportType.CANDIDATE,
            format=request.format,
            generated_at=datetime.now(),
            generated_by="system",  # This would come from current user
            download_url=download_url
        )

        return ReportResponse(
            success=True,
            message="Candidate report generated successfully",
            report_id=report_id,
            download_url=download_url,
            metadata=metadata
        )

    def _generate_interview_report(self, db: Session, request: ReportGenerationRequest) -> ReportResponse:
        """Generate interview report."""
        if not request.interview_id:
            return ReportResponse(success=False, message="Interview ID is required for interview reports")

        interview = self.interview_dao.get(db, request.interview_id)
        if not interview:
            return ReportResponse(success=False, message="Interview not found")

        # Mock report generation
        report_id = 2  # This would be generated from database
        download_url = f"/api/v1/reports/download/{report_id}"

        metadata = ReportMetadata(
            id=report_id,
            title=f"Interview Report - {interview.id}",
            report_type=ReportType.INTERVIEW,
            format=request.format,
            generated_at=datetime.now(),
            generated_by="system",
            download_url=download_url
        )

        return ReportResponse(
            success=True,
            message="Interview report generated successfully",
            report_id=report_id,
            download_url=download_url,
            metadata=metadata
        )

    def _generate_analytics_report(self, db: Session, request: ReportGenerationRequest) -> ReportResponse:
        """Generate analytics report."""
        # Mock report generation
        report_id = 3  # This would be generated from database
        download_url = f"/api/v1/reports/download/{report_id}"

        metadata = ReportMetadata(
            id=report_id,
            title="Analytics Report",
            report_type=ReportType.ANALYTICS,
            format=request.format,
            generated_at=datetime.now(),
            generated_by="system",
            download_url=download_url
        )

        return ReportResponse(
            success=True,
            message="Analytics report generated successfully",
            report_id=report_id,
            download_url=download_url,
            metadata=metadata
        )

    def _generate_custom_report(self, db: Session, request: ReportGenerationRequest) -> ReportResponse:
        """Generate custom report."""
        # Mock report generation
        report_id = 4  # This would be generated from database
        download_url = f"/api/v1/reports/download/{report_id}"

        metadata = ReportMetadata(
            id=report_id,
            title="Custom Report",
            report_type=ReportType.CUSTOM,
            format=request.format,
            generated_at=datetime.now(),
            generated_by="system",
            download_url=download_url
        )

        return ReportResponse(
            success=True,
            message="Custom report generated successfully",
            report_id=report_id,
            download_url=download_url,
            metadata=metadata
        )
