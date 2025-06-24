from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import StrEnum


class ReportFormat(StrEnum):
    """Report export formats."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ReportType(StrEnum):
    """Types of reports that can be generated."""
    CANDIDATE = "candidate"
    INTERVIEW = "interview"
    ANALYTICS = "analytics"
    CUSTOM = "custom"


class ChartType(StrEnum):
    """Types of charts for analytics."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class ReportFrequency(StrEnum):
    """Frequency options for scheduled reports."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ChartDataPoint(BaseModel):
    """Individual data point for charts."""
    label: str
    value: Union[int, float]
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChartData(BaseModel):
    """Chart data structure."""
    title: str
    chart_type: ChartType
    data: List[ChartDataPoint]
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    description: Optional[str] = None


class SummaryCard(BaseModel):
    """Summary card data for dashboard."""
    title: str
    value: Union[int, float, str]
    change: Optional[float] = None  # Percentage change
    change_direction: Optional[str] = None  # "up", "down", "neutral"
    description: Optional[str] = None
    icon: Optional[str] = None


class AnalyticsFilters(BaseModel):
    """Filters for analytics data."""
    date_range: Optional[Dict[str, datetime]] = None
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None
    department: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None


class OverviewData(BaseModel):
    """Overview dashboard data."""
    summary_cards: List[SummaryCard]
    trends_chart: ChartData
    risk_distribution_chart: ChartData
    department_breakdown_chart: ChartData
    recent_interviews: List[Dict[str, Any]]


class AnalyticsData(BaseModel):
    """Analytics dashboard data."""
    interview_volume_chart: ChartData
    risk_trends_chart: ChartData
    completion_rates_chart: ChartData
    score_distribution_chart: ChartData
    department_comparison_chart: ChartData
    time_to_complete_chart: ChartData
    filters_applied: Optional[AnalyticsFilters] = None


class ReportGenerationRequest(BaseModel):
    """Request to generate a report."""
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    candidate_id: Optional[int] = None
    interview_id: Optional[int] = None
    job_id: Optional[int] = None
    filters: Optional[AnalyticsFilters] = None
    include_charts: bool = True
    include_raw_data: bool = False
    email_recipients: Optional[List[str]] = None


class ReportMetadata(BaseModel):
    """Metadata for generated reports."""
    id: int
    title: str
    report_type: ReportType
    format: ReportFormat
    file_size: Optional[int] = None
    generated_at: datetime
    generated_by: str
    status: str = "completed"
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class CustomReportField(BaseModel):
    """Field definition for custom reports."""
    field_name: str
    display_name: str
    field_type: str  # "string", "number", "date", "boolean"
    is_required: bool = False
    description: Optional[str] = None


class CustomReportDefinition(BaseModel):
    """Definition for custom reports."""
    name: str
    description: Optional[str] = None
    data_source: str  # "interviews", "candidates", "jobs"
    selected_fields: List[CustomReportField]
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[str] = None
    sort_order: str = "asc"


class CustomReportRequest(BaseModel):
    """Request to create/run custom report."""
    definition: CustomReportDefinition
    format: ReportFormat = ReportFormat.CSV
    save_definition: bool = False


class ScheduledReportRequest(BaseModel):
    """Request to schedule a report."""
    report_type: ReportType
    frequency: ReportFrequency
    schedule_time: str  # HH:MM format
    recipients: List[str]
    filters: Optional[AnalyticsFilters] = None
    format: ReportFormat = ReportFormat.PDF
    is_enabled: bool = True


class ScheduledReport(BaseModel):
    """Scheduled report configuration."""
    id: int
    name: str
    report_type: ReportType
    frequency: ReportFrequency
    schedule_time: str
    recipients: List[str]
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    is_enabled: bool = True
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)


class ReportHistoryItem(BaseModel):
    """Report history item."""
    id: int
    title: str
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    generated_by: str
    file_size: Optional[int] = None
    download_count: int = 0
    status: str = "completed"
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportExportRequest(BaseModel):
    """Request to export existing report in different format."""
    report_id: int
    format: ReportFormat
    include_metadata: bool = True


class ReportResponse(BaseModel):
    """Generic report response."""
    success: bool
    message: str
    report_id: Optional[int] = None
    download_url: Optional[str] = None
    metadata: Optional[ReportMetadata] = None


class AnalyticsResponse(BaseModel):
    """Response for analytics endpoints."""
    success: bool
    data: Union[OverviewData, AnalyticsData]
    filters_applied: Optional[AnalyticsFilters] = None
    generated_at: datetime = Field(default_factory=datetime.now)


class ReportListResponse(BaseModel):
    """Response for report listing endpoints."""
    reports: List[ReportHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AvailableFieldsResponse(BaseModel):
    """Response for available fields for custom reports."""
    data_source: str
    fields: List[CustomReportField]
