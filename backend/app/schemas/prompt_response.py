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


class InterviewMessageResponse(BaseModel):
    """Response schema for interview message processing"""
    assistant_response: str


class QuestionEvaluationResponse(BaseModel):
    """Response schema for question evaluation"""
    reasoning: str
    question_fully_answered: bool
