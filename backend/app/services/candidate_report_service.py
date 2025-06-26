"""
AI-powered candidate report generation service using Claude Sonnet.
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.core.llm_service import LLMFactory, ModelName, LLMConfig
from app.crud.candidate_report import CandidateReportDAO
from app.crud.candidate import candidate_dao
from app.crud.interview_session import interview_session_dao
from app.schemas.candidate_report import CandidateReportCreate, RiskFactor, ReportGrade, RiskLevel
from pydantic import BaseModel, Field
from typing import List

logger = logging.getLogger(__name__)


class AIReportResponse(BaseModel):
    """Pydantic model for AI report generation response"""
    header: str = Field(..., description="Report header/title")
    risk_factors: List[dict] = Field(default_factory=list, description="List of risk factors with category, description, severity, and evidence")
    overall_risk_level: str = Field(..., description="Overall risk level: low, medium, high, or critical")
    general_observation: str = Field(..., description="General observations about the candidate")
    final_grade: str = Field(..., description="Final grade: excellent, good, satisfactory, poor, or fail")
    general_impression: str = Field(..., description="General impression and recommendation")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence in the assessment (0-1)")
    key_strengths: List[str] = Field(default_factory=list, description="Key strengths identified")
    areas_of_concern: List[str] = Field(default_factory=list, description="Areas requiring attention")


class CandidateReportService:
    """Service for generating AI-powered candidate reports"""

    def __init__(self):
        self.report_dao = CandidateReportDAO()
        # Use Claude Sonnet for report generation
        config = LLMConfig(
            max_tokens=4000,
            temperature=0.3,  # Lower temperature for more consistent reports
            top_p=0.9
        )
        self.llm_client = LLMFactory.create_client(ModelName.CLAUDE_4_SONNET, config)

    def generate_ai_report(self, db: Session, candidate_id: int) -> Optional[CandidateReportCreate]:
        """
        Generate an AI-powered candidate report based on interview conversation
        """
        logger.info(f"Starting AI report generation for candidate {candidate_id}")

        # Check if report already exists
        existing_report = self.report_dao.get_by_candidate_id(db=db, candidate_id=candidate_id)
        if existing_report:
            logger.info(f"Report already exists for candidate {candidate_id}")
            return None

        # Get candidate details
        candidate = candidate_dao.get(db=db, id=candidate_id)
        if not candidate:
            logger.warning(f"Candidate {candidate_id} not found")
            return None

        # Get interview session and conversation history
        sessions = interview_session_dao.get_sessions_by_candidate(db=db, candidate_id=candidate_id)
        if not sessions:
            logger.warning(f"No interview sessions found for candidate {candidate_id}")
            return None

        # Get the most recent completed session or the latest session
        target_session = None
        for s in sessions:
            if s.status.value == "completed":
                target_session = s
                break

        if not target_session:
            # If no completed session, get the latest session
            target_session = sessions[-1] if sessions else None

        if not target_session:
            logger.warning(f"No valid interview session found for candidate {candidate_id}")
            return None

        candidate_name = f"{candidate.first_name} {candidate.last_name}"
        logger.info(f"Generating AI report for candidate: {candidate_name}")

        try:
            # Get conversation history - it's stored as JSON in the database
            conversation_history = getattr(target_session, 'conversation_history', [])
            if not conversation_history:
                logger.warning(f"No conversation history found for candidate {candidate_id}")
                return None

            # Prepare conversation data for AI analysis
            conversation_text = self._format_conversation_for_analysis(conversation_history)
            
            # Generate AI report
            ai_response = self._generate_ai_evaluation(candidate_name, conversation_text)
            
            # Convert AI response to report data
            report_data = self._convert_ai_response_to_report(candidate_id, ai_response)
            
            # Save the report
            self.report_dao.create(db=db, obj_in=report_data)
            logger.info(f"Successfully generated AI report for candidate {candidate_id}")

            return report_data

        except Exception as e:
            logger.exception(f"Failed to generate AI report for candidate {candidate_id}: {e}")
            return None

    def _format_conversation_for_analysis(self, conversation_history) -> str:
        """Format conversation history for AI analysis"""
        formatted_messages = []

        for message in conversation_history:
            # Handle both ChatMessage objects and dict formats
            if hasattr(message, 'role'):
                # ChatMessage object
                role = message.role
                content = message.content
            else:
                # Dict format
                role = message.get("role", "unknown")
                content = message.get("content", "")

            if role == "assistant":
                formatted_messages.append(f"Interviewer: {content}")
            elif role == "user":
                formatted_messages.append(f"Candidate: {content}")

        return "\n\n".join(formatted_messages)

    def _generate_ai_evaluation(self, candidate_name: str, conversation_text: str) -> AIReportResponse:
        """Generate AI evaluation using Claude Sonnet"""
        
        prompt = f"""You are an expert HR professional conducting a comprehensive evaluation of a job candidate based on their interview conversation. 

Candidate Name: {candidate_name}

Interview Conversation:
{conversation_text}

Please analyze this interview conversation and provide a detailed assessment report. Your response must be in valid JSON format matching the following structure:

{{
    "header": "Interview Assessment Report - [Candidate Name]",
    "risk_factors": [
        {{
            "category": "Risk category name",
            "description": "Description of the risk factor",
            "severity": "low|medium|high|critical",
            "evidence": "Specific evidence or quotes from the conversation"
        }}
    ],
    "overall_risk_level": "low|medium|high|critical",
    "general_observation": "Detailed general observations about the candidate's performance",
    "final_grade": "excellent|good|satisfactory|poor|fail",
    "general_impression": "Overall impression and hiring recommendation",
    "confidence_score": 0.85,
    "key_strengths": ["List of key strengths identified"],
    "areas_of_concern": ["List of areas requiring attention"]
}}

Evaluation Guidelines:
1. Assess communication skills, professionalism, and engagement
2. Look for red flags like inappropriate behavior, dishonesty, or concerning attitudes
3. Evaluate responses for depth, relevance, and coherence
4. Consider cultural sensitivity and professional demeanor
5. Provide specific evidence from the conversation to support your assessment
6. Be objective and fair in your evaluation
7. The confidence_score should reflect how certain you are about your assessment (0.0-1.0)

Ensure your response is valid JSON that matches the exact structure above."""

        try:
            # Generate response using Claude Sonnet
            response = self.llm_client.generate(prompt, AIReportResponse)
            return response
        except Exception as e:
            logger.exception(f"Error generating AI evaluation: {e}")
            # Return a fallback response
            return AIReportResponse(
                header=f"Interview Assessment Report - {candidate_name}",
                risk_factors=[],
                overall_risk_level="medium",
                general_observation="Unable to complete full AI analysis due to technical issues. Manual review recommended.",
                final_grade="satisfactory",
                general_impression="Technical issues prevented complete AI analysis. Please conduct manual review.",
                confidence_score=0.3,
                key_strengths=["Participated in interview process"],
                areas_of_concern=["Requires manual review due to AI analysis failure"]
            )

    def _convert_ai_response_to_report(self, candidate_id: int, ai_response: AIReportResponse) -> CandidateReportCreate:
        """Convert AI response to CandidateReportCreate object"""
        
        # Convert risk factors from dict to RiskFactor objects
        risk_factors = []
        for rf_dict in ai_response.risk_factors:
            try:
                risk_factor = RiskFactor(
                    category=rf_dict.get("category", "General"),
                    description=rf_dict.get("description", "No description provided"),
                    severity=RiskLevel(rf_dict.get("severity", "low")),
                    evidence=rf_dict.get("evidence")
                )
                risk_factors.append(risk_factor)
            except Exception as e:
                logger.warning(f"Error converting risk factor: {e}")
                continue

        # Convert overall risk level
        try:
            overall_risk_level = RiskLevel(ai_response.overall_risk_level)
        except ValueError:
            logger.warning(f"Invalid risk level: {ai_response.overall_risk_level}, defaulting to medium")
            overall_risk_level = RiskLevel.MEDIUM

        # Convert final grade
        try:
            final_grade = ReportGrade(ai_response.final_grade)
        except ValueError:
            logger.warning(f"Invalid grade: {ai_response.final_grade}, defaulting to satisfactory")
            final_grade = ReportGrade.SATISFACTORY

        return CandidateReportCreate(
            candidate_id=candidate_id,
            header=ai_response.header,
            risk_factors=risk_factors,
            overall_risk_level=overall_risk_level,
            general_observation=ai_response.general_observation,
            final_grade=final_grade,
            general_impression=ai_response.general_impression,
            confidence_score=ai_response.confidence_score,
            key_strengths=ai_response.key_strengths,
            areas_of_concern=ai_response.areas_of_concern
        )
