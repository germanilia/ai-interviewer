"""
Unit tests for ReportsService.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

from app.services.reports_service import ReportsService
from app.schemas.reports import AnalyticsFilters, ChartType
from app.crud.interview import InterviewDAO
from app.crud.candidate import CandidateDAO
from app.crud.job import JobDAO
from app.crud.reports import ReportsDAO


class TestReportsService:
    """Test cases for ReportsService."""

    @pytest.fixture
    def mock_daos(self):
        """Create mock DAOs."""
        return {
            'interview_dao': Mock(spec=InterviewDAO),
            'candidate_dao': Mock(spec=CandidateDAO),
            'job_dao': Mock(spec=JobDAO),
            'reports_dao': Mock(spec=ReportsDAO)
        }

    @pytest.fixture
    def reports_service(self, mock_daos):
        """Create ReportsService with mock DAOs."""
        return ReportsService(
            interview_dao=mock_daos['interview_dao'],
            candidate_dao=mock_daos['candidate_dao'],
            job_dao=mock_daos['job_dao'],
            reports_dao=mock_daos['reports_dao']
        )

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()

    def test_get_overview_data_success(self, reports_service, mock_daos, mock_db):
        """Test successful overview data generation."""
        # Mock DAO responses
        mock_daos['reports_dao'].get_summary_statistics.return_value = {
            "total_interviews": 100,
            "completed_interviews": 80,
            "completion_rate": 80.0,
            "avg_score": 75.5,
            "flagged_candidates": 5
        }
        
        mock_daos['reports_dao'].get_monthly_trends.return_value = [
            {"month": datetime(2024, 1, 1), "count": 20},
            {"month": datetime(2024, 2, 1), "count": 25}
        ]
        
        mock_daos['reports_dao'].get_risk_distribution.return_value = [
            {"risk_level": "low", "count": 60},
            {"risk_level": "medium", "count": 30},
            {"risk_level": "high", "count": 10}
        ]
        
        mock_daos['reports_dao'].get_department_breakdown.return_value = [
            {"department": "Engineering", "count": 50},
            {"department": "Sales", "count": 30}
        ]
        
        mock_interview = Mock()
        mock_interview.id = 1
        mock_interview.candidate.first_name = "John"
        mock_interview.candidate.last_name = "Doe"
        mock_interview.job.title = "Engineer"
        mock_interview.status.value = "completed"
        mock_interview.created_at = datetime.now()
        
        mock_daos['reports_dao'].get_recent_interviews.return_value = [mock_interview]

        # Test
        result = reports_service.get_overview_data(mock_db)

        # Assertions
        assert result is not None
        assert len(result.summary_cards) == 4
        assert result.summary_cards[0].title == "Total Interviews"
        assert result.summary_cards[0].value == 100
        assert result.trends_chart.title == "Interview Trends"
        assert result.trends_chart.chart_type == ChartType.LINE
        assert len(result.recent_interviews) == 1

    def test_get_overview_data_with_filters(self, reports_service, mock_daos, mock_db):
        """Test overview data generation with filters."""
        filters = AnalyticsFilters(
            candidate_id=1,
            job_id=2,
            department="Engineering"
        )

        # Mock DAO responses
        mock_daos['reports_dao'].get_summary_statistics.return_value = {
            "total_interviews": 50,
            "completed_interviews": 40,
            "completion_rate": 80.0,
            "avg_score": 78.0,
            "flagged_candidates": 2
        }
        
        mock_daos['reports_dao'].get_monthly_trends.return_value = []
        mock_daos['reports_dao'].get_risk_distribution.return_value = []
        mock_daos['reports_dao'].get_department_breakdown.return_value = []
        mock_daos['reports_dao'].get_recent_interviews.return_value = []

        # Test
        result = reports_service.get_overview_data(mock_db, filters)

        # Assertions
        assert result is not None
        mock_daos['reports_dao'].get_summary_statistics.assert_called_once_with(mock_db, filters)

    def test_get_analytics_data_success(self, reports_service, mock_daos, mock_db):
        """Test successful analytics data generation."""
        # Mock DAO responses
        mock_daos['reports_dao'].get_daily_volume.return_value = [
            {"day": datetime(2024, 1, 1), "count": 5},
            {"day": datetime(2024, 1, 2), "count": 8}
        ]
        
        mock_daos['reports_dao'].get_weekly_risk_trends.return_value = [
            {"week": datetime(2024, 1, 1), "count": 2}
        ]
        
        mock_daos['reports_dao'].get_monthly_completion_rates.return_value = [
            {"month": datetime(2024, 1, 1), "total": 20, "completed": 16, "rate": 80.0}
        ]
        
        mock_daos['reports_dao'].get_score_distribution.return_value = [
            {"range": "0-20", "count": 5},
            {"range": "21-40", "count": 10}
        ]
        
        mock_daos['reports_dao'].get_department_avg_scores.return_value = [
            {"department": "Engineering", "avg_score": 85.0}
        ]
        
        mock_daos['reports_dao'].get_completion_time_distribution.return_value = [
            {"range": "0-15 min", "count": 10}
        ]

        # Test
        result = reports_service.get_analytics_data(mock_db)

        # Assertions
        assert result is not None
        assert result.interview_volume_chart.title == "Interview Volume (Last 30 Days)"
        assert result.risk_trends_chart.title == "High Risk Trends (Last 12 Weeks)"
        assert result.completion_rates_chart.title == "Completion Rates (Last 6 Months)"
        assert result.score_distribution_chart.title == "Score Distribution"
        assert result.department_comparison_chart.title == "Average Scores by Department"
        assert result.time_to_complete_chart.title == "Time to Complete Distribution"

    def test_generate_candidate_report_success(self, reports_service, mock_daos, mock_db):
        """Test successful candidate report generation."""
        from app.schemas.reports import ReportGenerationRequest, ReportType, ReportFormat
        
        # Mock candidate
        mock_candidate = Mock()
        mock_candidate.first_name = "John"
        mock_candidate.last_name = "Doe"
        mock_daos['candidate_dao'].get.return_value = mock_candidate

        request = ReportGenerationRequest(
            report_type=ReportType.CANDIDATE,
            format=ReportFormat.PDF,
            candidate_id=1
        )

        # Test
        result = reports_service.generate_report(mock_db, request)

        # Assertions
        assert result.success is True
        assert "Candidate Report - John Doe" in result.metadata.title
        assert result.metadata.report_type == ReportType.CANDIDATE
        assert result.metadata.format == ReportFormat.PDF

    def test_generate_candidate_report_not_found(self, reports_service, mock_daos, mock_db):
        """Test candidate report generation when candidate not found."""
        from app.schemas.reports import ReportGenerationRequest, ReportType, ReportFormat
        
        # Mock candidate not found
        mock_daos['candidate_dao'].get.return_value = None

        request = ReportGenerationRequest(
            report_type=ReportType.CANDIDATE,
            format=ReportFormat.PDF,
            candidate_id=999
        )

        # Test
        result = reports_service.generate_report(mock_db, request)

        # Assertions
        assert result.success is False
        assert "Candidate not found" in result.message

    def test_generate_interview_report_success(self, reports_service, mock_daos, mock_db):
        """Test successful interview report generation."""
        from app.schemas.reports import ReportGenerationRequest, ReportType, ReportFormat
        
        # Mock interview
        mock_interview = Mock()
        mock_interview.id = 1
        mock_daos['interview_dao'].get.return_value = mock_interview

        request = ReportGenerationRequest(
            report_type=ReportType.INTERVIEW,
            format=ReportFormat.EXCEL,
            interview_id=1
        )

        # Test
        result = reports_service.generate_report(mock_db, request)

        # Assertions
        assert result.success is True
        assert "Interview Report - 1" in result.metadata.title
        assert result.metadata.report_type == ReportType.INTERVIEW
        assert result.metadata.format == ReportFormat.EXCEL

    def test_get_available_fields_interviews(self, reports_service):
        """Test getting available fields for interviews data source."""
        result = reports_service.get_available_fields("interviews")

        assert result.data_source == "interviews"
        assert len(result.fields) > 0
        
        # Check for expected fields
        field_names = [field.field_name for field in result.fields]
        assert "id" in field_names
        assert "status" in field_names
        assert "score" in field_names
        assert "candidate_name" in field_names

    def test_get_available_fields_candidates(self, reports_service):
        """Test getting available fields for candidates data source."""
        result = reports_service.get_available_fields("candidates")

        assert result.data_source == "candidates"
        assert len(result.fields) > 0
        
        # Check for expected fields
        field_names = [field.field_name for field in result.fields]
        assert "id" in field_names
        assert "first_name" in field_names
        assert "last_name" in field_names
        assert "email" in field_names

    def test_get_available_fields_jobs(self, reports_service):
        """Test getting available fields for jobs data source."""
        result = reports_service.get_available_fields("jobs")

        assert result.data_source == "jobs"
        assert len(result.fields) > 0
        
        # Check for expected fields
        field_names = [field.field_name for field in result.fields]
        assert "id" in field_names
        assert "title" in field_names
        assert "department" in field_names

    def test_build_summary_cards(self, reports_service):
        """Test building summary cards from statistics."""
        stats = {
            "total_interviews": 100,
            "completed_interviews": 80,
            "completion_rate": 80.0,
            "avg_score": 75.5,
            "flagged_candidates": 5
        }

        result = reports_service._build_summary_cards(stats)

        assert len(result) == 4
        assert result[0].title == "Total Interviews"
        assert result[0].value == 100
        assert result[1].title == "Completion Rate"
        assert result[1].value == "80.0%"
        assert result[2].title == "Average Risk Score"
        assert result[2].value == "75.5"
        assert result[3].title == "Flagged Candidates"
        assert result[3].value == 5

    def test_build_trends_chart(self, reports_service):
        """Test building trends chart from monthly data."""
        monthly_data = [
            {"month": datetime(2024, 1, 1), "count": 20},
            {"month": datetime(2024, 2, 1), "count": 25}
        ]

        result = reports_service._build_trends_chart(monthly_data)

        assert result.title == "Interview Trends"
        assert result.chart_type == ChartType.LINE
        assert len(result.data) == 2
        assert result.data[0].label == "2024-01"
        assert result.data[0].value == 20
