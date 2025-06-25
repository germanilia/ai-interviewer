from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text, case

from app.models.interview import Interview, InterviewStatus, RiskLevel, IntegrityScore
from app.models.candidate import Candidate

from app.schemas.reports import AnalyticsFilters
from app.core.config_service import config_service


class ReportsDAO:
    """Data Access Object for reports and analytics."""

    def _get_date_trunc_func(self, period: str, column):
        """Get database-specific date truncation function."""
        db_url = config_service.get_database_url()

        if db_url.startswith("sqlite"):
            # SQLite date functions
            if period == "day":
                return func.date(column)
            elif period == "week":
                # SQLite week calculation: start of week (Monday)
                return func.date(column, "weekday 1", "-6 days")
            elif period == "month":
                return func.date(column, "start of month")
            else:
                return func.date(column)
        else:
            # PostgreSQL date_trunc function
            return func.date_trunc(period, column)

    def _format_date_result(self, date_value):
        """Format date result from database query."""
        if isinstance(date_value, str):
            # SQLite returns strings, convert to datetime
            try:
                return datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                # If parsing fails, return the string as is
                return date_value
        elif hasattr(date_value, 'strftime'):
            # Already a datetime object
            return date_value
        else:
            # Return as is if we can't format it
            return date_value

    def get_interviews_with_filters(
        self, 
        db: Session, 
        filters: Optional[AnalyticsFilters] = None
    ) -> List[Interview]:
        """Get interviews with applied filters."""
        query = db.query(Interview).join(Candidate)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        return query.all()

    def get_summary_statistics(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> Dict[str, Any]:
        """Get summary statistics for dashboard cards."""
        query = db.query(Interview)

        # Department filtering is now done through interview.job_department
        # No need to join Job table since job info is in Interview

        if filters:
            query = self._apply_filters(query, filters)
        
        # Get basic counts
        total_interviews = query.count()
        completed_interviews = query.filter(Interview.status == InterviewStatus.COMPLETED).count()
        
        # Get average score
        avg_score_result = query.filter(Interview.score.isnot(None)).with_entities(
            func.avg(Interview.score)
        ).scalar()
        avg_score = float(avg_score_result) if avg_score_result else 0.0
        
        # Get flagged candidates count
        flagged_count = query.filter(
            Interview.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).count()
        
        completion_rate = (completed_interviews / total_interviews * 100) if total_interviews > 0 else 0
        
        return {
            "total_interviews": total_interviews,
            "completed_interviews": completed_interviews,
            "completion_rate": completion_rate,
            "avg_score": avg_score,
            "flagged_candidates": flagged_count
        }

    def get_monthly_trends(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get monthly interview trends."""
        month_func = self._get_date_trunc_func('month', Interview.interview_date)

        query = db.query(
            month_func.label('month'),
            func.count(Interview.id).label('count')
        ).filter(Interview.interview_date.isnot(None))

        # Add JOIN if we might need it for filtering
        # Department filtering is now done through interview.job_department
        # No need to join Job table since job info is in Interview

        if filters:
            query = self._apply_filters(query, filters)

        query = query.group_by(month_func)
        query = query.order_by(month_func)

        results = query.all()
        return [{"month": self._format_date_result(result.month), "count": result.count} for result in results]

    def get_risk_distribution(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get risk level distribution."""
        query = db.query(
            Interview.risk_level,
            func.count(Interview.id).label('count')
        ).filter(Interview.risk_level.isnot(None))
        
        if filters:
            query = self._apply_filters(query, filters)
        
        query = query.group_by(Interview.risk_level)
        
        results = query.all()
        return [{"risk_level": result.risk_level.value, "count": result.count} for result in results]

    def get_department_breakdown(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get department breakdown."""
        query = db.query(
            Interview.job_department,
            func.count(Interview.id).label('count')
        ).filter(Interview.job_department.isnot(None))

        if filters:
            query = self._apply_filters(query, filters)

        query = query.group_by(Interview.job_department)
        
        results = query.all()
        return [{"department": result.department, "count": result.count} for result in results]

    def get_daily_volume(self, db: Session, days: int = 30, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get daily interview volume for the last N days."""
        day_func = self._get_date_trunc_func('day', Interview.interview_date)

        query = db.query(
            day_func.label('day'),
            func.count(Interview.id).label('count')
        ).filter(Interview.interview_date.isnot(None))

        if filters:
            query = self._apply_filters(query, filters)

        # Filter for last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(Interview.interview_date >= cutoff_date)

        query = query.group_by(day_func)
        query = query.order_by(day_func)

        results = query.all()
        return [{"day": self._format_date_result(result.day), "count": result.count} for result in results]

    def get_weekly_risk_trends(self, db: Session, weeks: int = 12, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get weekly high-risk interview trends."""
        week_func = self._get_date_trunc_func('week', Interview.interview_date)

        query = db.query(
            week_func.label('week'),
            func.count(Interview.id).label('count')
        ).filter(
            and_(
                Interview.interview_date.isnot(None),
                Interview.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
            )
        )

        if filters:
            query = self._apply_filters(query, filters)

        # Filter for last N weeks
        cutoff_date = datetime.now() - timedelta(weeks=weeks)
        query = query.filter(Interview.interview_date >= cutoff_date)

        query = query.group_by(week_func)
        query = query.order_by(week_func)

        results = query.all()
        return [{"week": self._format_date_result(result.week), "count": result.count} for result in results]

    def get_monthly_completion_rates(self, db: Session, months: int = 6, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get monthly completion rates."""
        month_func = self._get_date_trunc_func('month', Interview.interview_date)

        query = db.query(
            month_func.label('month'),
            func.count(Interview.id).label('total'),
            func.sum(case((Interview.status == InterviewStatus.COMPLETED, 1), else_=0)).label('completed')
        ).filter(Interview.interview_date.isnot(None))

        if filters:
            query = self._apply_filters(query, filters)

        # Filter for last N months
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        query = query.filter(Interview.interview_date >= cutoff_date)

        query = query.group_by(month_func)
        query = query.order_by(month_func)

        results = query.all()
        return [
            {
                "month": self._format_date_result(result.month),
                "total": result.total,
                "completed": result.completed,
                "rate": (result.completed / result.total * 100) if result.total > 0 else 0
            }
            for result in results
        ]

    def get_score_distribution(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get score distribution in ranges."""
        query = db.query(Interview.score).filter(Interview.score.isnot(None))
        
        if filters:
            query = self._apply_filters(query, filters)
        
        scores = [result.score for result in query.all()]
        
        # Group into ranges
        ranges = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for score in scores:
            if score <= 20:
                ranges["0-20"] += 1
            elif score <= 40:
                ranges["21-40"] += 1
            elif score <= 60:
                ranges["41-60"] += 1
            elif score <= 80:
                ranges["61-80"] += 1
            else:
                ranges["81-100"] += 1
        
        return [{"range": range_name, "count": count} for range_name, count in ranges.items()]

    def get_department_avg_scores(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get average scores by department."""
        query = db.query(
            Interview.job_department,
            func.avg(Candidate.score).label('avg_score')
        ).join(Candidate).filter(
            and_(
                Interview.job_department.isnot(None),
                Candidate.score.isnot(None)
            )
        )

        if filters:
            query = self._apply_filters(query, filters)

        query = query.group_by(Interview.job_department)
        
        results = query.all()
        return [
            {"department": result.department, "avg_score": float(result.avg_score)}
            for result in results
        ]

    def get_completion_time_distribution(self, db: Session, filters: Optional[AnalyticsFilters] = None) -> List[Dict[str, Any]]:
        """Get completion time distribution."""
        query = db.query(
            Interview.interview_date,
            Interview.completed_at
        ).filter(
            and_(
                Interview.interview_date.isnot(None),
                Interview.completed_at.isnot(None)
            )
        )
        
        if filters:
            query = self._apply_filters(query, filters)
        
        results = query.all()
        
        # Calculate completion times in minutes
        completion_times = []
        for result in results:
            time_diff = result.completed_at - result.interview_date
            completion_times.append(time_diff.total_seconds() / 60)
        
        # Group into ranges
        ranges = {"0-15 min": 0, "16-30 min": 0, "31-45 min": 0, "46-60 min": 0, "60+ min": 0}
        for time_minutes in completion_times:
            if time_minutes <= 15:
                ranges["0-15 min"] += 1
            elif time_minutes <= 30:
                ranges["16-30 min"] += 1
            elif time_minutes <= 45:
                ranges["31-45 min"] += 1
            elif time_minutes <= 60:
                ranges["46-60 min"] += 1
            else:
                ranges["60+ min"] += 1
        
        return [{"range": range_name, "count": count} for range_name, count in ranges.items()]

    def get_recent_interviews(self, db: Session, limit: int = 5) -> List[Interview]:
        """Get recent interviews with related data."""
        return db.query(Interview).join(Candidate).order_by(
            desc(Interview.created_at)
        ).limit(limit).all()

    def _apply_filters(self, query, filters: AnalyticsFilters):
        """Apply filters to the query."""
        if filters.date_range:
            if "from" in filters.date_range:
                query = query.filter(Interview.interview_date >= filters.date_range["from"])
            if "to" in filters.date_range:
                query = query.filter(Interview.interview_date <= filters.date_range["to"])

        if filters.candidate_id:
            query = query.filter(Interview.candidate_id == filters.candidate_id)

        if filters.department:
            query = query.filter(Interview.job_department == filters.department)

        if filters.risk_level:
            query = query.filter(Candidate.risk_level == filters.risk_level)

        if filters.status:
            query = query.filter(Candidate.interview_status == filters.status)

        return query
