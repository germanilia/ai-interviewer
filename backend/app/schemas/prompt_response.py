"""
Response schemas for prompt execution results.
"""
from pydantic import BaseModel
from typing import Optional


class EvaluationResponse(BaseModel):
    """Response schema for Evaluation prompt execution"""
    reasoning: str
    response: str
    was_question_answered: bool
    interview_complete: bool
    answered_question_index: Optional[int] = None


class JudgeResponse(BaseModel):
    """Response schema for Judge prompt execution"""
    reasoning: str
    response: str
    was_question_answered: bool
    answered_question_index: Optional[int] = None


class GuardrailsResponse(BaseModel):
    """Response schema for Guardrails prompt execution"""
    can_continue: bool
    reason: Optional[str] = None
