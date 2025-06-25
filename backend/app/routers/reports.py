from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.dependencies import get_db, get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.reports import (
    AnalyticsFilters, ReportFormat, ReportGenerationRequest,
    ReportResponse, AnalyticsResponse, CustomReportRequest, ReportType, ReportFormat,
    ScheduledReportRequest, ReportListResponse, AvailableFieldsResponse,
    ReportExportRequest, ReportHistoryItem
)
from app.services.reports_service import ReportsService
from app.crud.interview import InterviewDAO
from app.crud.candidate import CandidateDAO
from app.crud.reports import ReportsDAO
from app.core.logging_service import get_logger

logger = get_logger(__name__)

reports_router = APIRouter()


def parse_date_string(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None


def get_reports_service() -> ReportsService:
    """Dependency to get ReportsService instance."""
    return ReportsService(
        interview_dao=InterviewDAO(),
        candidate_dao=CandidateDAO(),
        reports_dao=ReportsDAO()
    )


@reports_router.get("/reports/overview", response_model=AnalyticsResponse)
async def get_overview_data(
    date_from: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    candidate_id: Optional[int] = Query(None, description="Filter by candidate ID"),
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    reports_service: ReportsService = Depends(get_reports_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get overview dashboard data with summary cards and charts.
    """
    try:
        # Build filters
        filters = None
        if any([date_from, date_to, candidate_id, job_id, department, risk_level, status]):
            date_range = None
            if date_from or date_to:
                date_range = {}
                if date_from:
                    parsed_from = parse_date_string(date_from)
                    if parsed_from:
                        date_range["from"] = parsed_from
                if date_to:
                    parsed_to = parse_date_string(date_to)
                    if parsed_to:
                        date_range["to"] = parsed_to

            filters = AnalyticsFilters(
                date_range=date_range,
                candidate_id=candidate_id,
                job_id=job_id,
                department=department,
                risk_level=risk_level,
                status=status
            )

        overview_data = reports_service.get_overview_data(db=db, filters=filters)
        
        return AnalyticsResponse(
            success=True,
            data=overview_data,
            filters_applied=filters
        )
    except Exception as e:
        logger.error(f"Error getting overview data: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve overview data: {str(e)}"
        )


@reports_router.get("/reports/analytics", response_model=AnalyticsResponse)
async def get_analytics_data(
    date_from: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    candidate_id: Optional[int] = Query(None, description="Filter by candidate ID"),
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    reports_service: ReportsService = Depends(get_reports_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get analytics dashboard data with detailed charts.
    """
    try:
        # Build filters
        filters = None
        if any([date_from, date_to, candidate_id, job_id, department, risk_level, status]):
            date_range = None
            if date_from or date_to:
                date_range = {}
                if date_from:
                    parsed_from = parse_date_string(date_from)
                    if parsed_from:
                        date_range["from"] = parsed_from
                if date_to:
                    parsed_to = parse_date_string(date_to)
                    if parsed_to:
                        date_range["to"] = parsed_to

            filters = AnalyticsFilters(
                date_range=date_range,
                candidate_id=candidate_id,
                job_id=job_id,
                department=department,
                risk_level=risk_level,
                status=status
            )

        analytics_data = reports_service.get_analytics_data(db=db, filters=filters)
        
        return AnalyticsResponse(
            success=True,
            data=analytics_data,
            filters_applied=filters
        )
    except Exception as e:
        logger.error(f"Error getting analytics data: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics data: {str(e)}"
        )


@reports_router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerationRequest,
    db: Session = Depends(get_db),
    reports_service: ReportsService = Depends(get_reports_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Generate a report based on the request parameters.
    """
    try:
        logger.info(f"Generating {request.report_type} report for user {current_user.email}")
        
        response = reports_service.generate_report(db=db, request=request)
        
        if not response.success:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@reports_router.get("/reports/fields/{data_source}", response_model=AvailableFieldsResponse)
async def get_available_fields(
    data_source: str,
    reports_service: ReportsService = Depends(get_reports_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get available fields for custom report building.
    """
    try:
        if data_source not in ["interviews", "candidates", "jobs"]:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Invalid data source. Must be one of: interviews, candidates, jobs"
            )
        
        return reports_service.get_available_fields(data_source)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available fields: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve available fields: {str(e)}"
        )


@reports_router.post("/reports/custom", response_model=ReportResponse)
async def create_custom_report(
    request: CustomReportRequest,
    db: Session = Depends(get_db),
    reports_service: ReportsService = Depends(get_reports_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create and run a custom report.
    """
    try:
        # Convert custom report request to standard report generation request
        report_request = ReportGenerationRequest(
            report_type=ReportType.CUSTOM,
            format=request.format,
            filters=None  # Custom reports handle their own filtering
        )
        
        response = reports_service.generate_report(db=db, request=report_request)
        
        if not response.success:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating custom report: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom report: {str(e)}"
        )


@reports_router.get("/reports/history", response_model=ReportListResponse)
async def get_report_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get report generation history.
    """
    try:
        # Mock data for now - in real implementation, this would query the database
        mock_reports = [
            ReportHistoryItem(
                id=1,
                title="Candidate Report - John Smith",
                report_type=ReportType.CANDIDATE,
                format=ReportFormat.PDF,
                generated_at=datetime(2024, 1, 15, 10, 30, 0),
                generated_by=current_user.email,
                file_size=1024000,
                download_count=3,
                status="completed",
                download_url="/api/v1/reports/download/1"
            ),
            ReportHistoryItem(
                id=2,
                title="Analytics Report",
                report_type=ReportType.ANALYTICS,
                format=ReportFormat.EXCEL,
                generated_at=datetime(2024, 1, 14, 15, 45, 0),
                generated_by=current_user.email,
                file_size=2048000,
                download_count=1,
                status="completed",
                download_url="/api/v1/reports/download/2"
            )
        ]
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_reports = mock_reports[start_idx:end_idx]
        
        total = len(mock_reports)
        total_pages = (total + page_size - 1) // page_size
        
        return ReportListResponse(
            reports=paginated_reports,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error getting report history: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report history: {str(e)}"
        )


@reports_router.post("/reports/export", response_model=ReportResponse)
async def export_report(
    request: ReportExportRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Export an existing report in a different format.
    """
    try:
        # Mock export functionality
        download_url = f"/api/v1/reports/download/{request.report_id}?format={request.format}"

        return ReportResponse(
            success=True,
            message=f"Report exported successfully in {request.format} format",
            report_id=request.report_id,
            download_url=download_url
        )
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export report: {str(e)}"
        )


@reports_router.get("/reports/download/{report_id}")
async def download_report(
    report_id: int,
    format: Optional[str] = Query(None, description="Export format"),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Download a generated report.
    """
    try:
        # Mock download functionality
        # In real implementation, this would serve the actual file
        return {
            "message": f"Report {report_id} download initiated",
            "format": format or "original",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download report: {str(e)}"
        )


@reports_router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a report from history.
    """
    try:
        # Mock delete functionality
        return {
            "message": f"Report {report_id} deleted successfully",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )


@reports_router.post("/reports/schedule", response_model=dict)
async def schedule_report(
    request: ScheduledReportRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Schedule a report to be generated automatically.
    """
    try:
        # Mock scheduling functionality
        return {
            "message": "Report scheduled successfully",
            "schedule_id": 1,
            "frequency": request.frequency,
            "next_run": "2024-01-16T09:00:00Z",
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error scheduling report: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule report: {str(e)}"
        )


@reports_router.get("/reports/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    date_from: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
    reports_service: ReportsService = Depends(get_reports_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get specific chart data for analytics dashboard.
    """
    try:
        # Build filters
        filters = None
        if any([date_from, date_to, department]):
            date_range = None
            if date_from or date_to:
                date_range = {}
                if date_from:
                    parsed_from = parse_date_string(date_from)
                    if parsed_from:
                        date_range["from"] = parsed_from
                if date_to:
                    parsed_to = parse_date_string(date_to)
                    if parsed_to:
                        date_range["to"] = parsed_to

            filters = AnalyticsFilters(
                date_range=date_range,
                department=department
            )

        # Get analytics data and extract specific chart
        analytics_data = reports_service.get_analytics_data(db=db, filters=filters)

        chart_map = {
            "interview-volume": analytics_data.interview_volume_chart,
            "risk-trends": analytics_data.risk_trends_chart,
            "completion-rates": analytics_data.completion_rates_chart,
            "score-distribution": analytics_data.score_distribution_chart,
            "department-comparison": analytics_data.department_comparison_chart,
            "time-to-complete": analytics_data.time_to_complete_chart
        }

        if chart_type not in chart_map:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid chart type. Available types: {', '.join(chart_map.keys())}"
            )

        return {
            "success": True,
            "chart_data": chart_map[chart_type],
            "filters_applied": filters
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chart data: {str(e)}"
        )
