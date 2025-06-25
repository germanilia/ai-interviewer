"""
LLM service for interview conversations with hard-coded responses.
"""
import logging
from typing import Optional, Tuple, TYPE_CHECKING
from app.schemas.interview_session import InterviewContext, ChatMessage
from app.core.llm_service import LLMConfig, LLMFactory, ModelName, ReasoningConfig

if TYPE_CHECKING:
    from app.schemas.question import QuestionResponse

logger = logging.getLogger(__name__)


class InterviewLLMService:
    """Service for handling LLM interactions during interviews"""

    def __init__(self):
        llm_config_reasoning = LLMConfig(reasoning=ReasoningConfig(enabled=True, budget_tokens=1000))
        self.small_llm = LLMFactory.create_client(model_name=ModelName.CLAUDE_3_5_HAIKU)
        self.judge_llm = LLMFactory.create_client(model_name=ModelName.CLAUDE_4_SONNET, config=llm_config_reasoning)
        self.guardian_llm = LLMFactory.create_client(model_name=ModelName.CLAUDE_3_5_HAIKU)
        self.hard_coded_responses = {
            "en": [
                "Thank you for that response. Can you tell me more about your background and experience?",
                "That's interesting. How do you handle challenging situations at work?",
                "I appreciate your honesty. Can you describe a time when you faced an ethical dilemma?",
                "Thank you for sharing that. How do you prioritize your work when you have multiple deadlines?",
                "That's a good point. Can you tell me about a time when you had to work with a difficult colleague?",
                "I understand. How do you handle stress and pressure in the workplace?",
                "Thank you for that insight. Can you describe your approach to problem-solving?",
                "That's helpful. How do you ensure accuracy and attention to detail in your work?",
                "I see. Can you tell me about a time when you had to learn something new quickly?",
                "Thank you for your response. How do you handle feedback and criticism?"
            ],
            "he": [
                "תודה על התשובה. אתה יכול לספר לי יותר על הרקע והניסיון שלך?",
                "זה מעניין. איך אתה מתמודד עם מצבים מאתגרים בעבודה?",
                "אני מעריך את הכנות שלך. אתה יכול לתאר זמן שבו התמודדת עם דילמה אתית?",
                "תודה על השיתוף. איך אתה מתעדף את העבודה שלך כשיש לך כמה דדליינים?",
                "זו נקודה טובה. אתה יכול לספר לי על זמן שבו היית צריך לעבוד עם עמית קשה?",
                "אני מבין. איך אתה מתמודד עם לחץ ומתח במקום העבודה?",
                "תודה על התובנה. אתה יכול לתאר את הגישה שלך לפתרון בעיות?",
                "זה מועיל. איך אתה מבטיח דיוק ותשומת לב לפרטים בעבודה שלך?",
                "אני רואה. אתה יכול לספר לי על זמן שבו היית צריך ללמוד משהו חדש במהירות?",
                "תודה על התשובה שלך. איך אתה מתמודד עם משוב וביקורת?"
            ],
            "ar": [
                "شكراً لك على هذه الإجابة. هل يمكنك أن تخبرني المزيد عن خلفيتك وخبرتك؟",
                "هذا مثير للاهتمام. كيف تتعامل مع المواقف الصعبة في العمل؟",
                "أقدر صدقك. هل يمكنك وصف وقت واجهت فيه معضلة أخلاقية؟",
                "شكراً لك على المشاركة. كيف تحدد أولويات عملك عندما يكون لديك مواعيد نهائية متعددة؟",
                "هذه نقطة جيدة. هل يمكنك أن تخبرني عن وقت اضطررت فيه للعمل مع زميل صعب؟",
                "أفهم ذلك. كيف تتعامل مع التوتر والضغط في مكان العمل؟",
                "شكراً لك على هذه البصيرة. هل يمكنك وصف نهجك في حل المشكلات؟",
                "هذا مفيد. كيف تضمن الدقة والانتباه للتفاصيل في عملك؟",
                "أرى ذلك. هل يمكنك أن تخبرني عن وقت اضطررت فيه لتعلم شيء جديد بسرعة؟",
                "شكراً لك على إجابتك. كيف تتعامل مع التعليقات والنقد؟"
            ]
        }
        self.response_index = 0

    def process_interview_message(
        self,
        context: InterviewContext,
        user_message: str,
        language: str = "en"
    ) -> Tuple[str, bool]:
        """
        Process user message and return LLM response and completion status
        
        Args:
            context: Interview context with candidate info and conversation history
            user_message: The user's message
            
        Returns:
            Tuple of (assistant_response, is_interview_complete)
        """
        logger.info(f"Processing message for candidate: {context.candidate_name}")
        
        # Check if user wants to end the interview
        if self._is_completion_message(user_message):
            return self._generate_completion_response(context, language), True

        # Generate next response
        response = self._generate_response(context, user_message, language)
        return response, False

    def _is_completion_message(self, message: str) -> bool:
        """Check if the message indicates the user wants to end the interview"""
        completion_keywords = [
            "done", "finished", "complete", "end", "that's all", 
            "no more", "i'm done", "finish", "conclude"
        ]
        message_lower = message.lower().strip()
        return any(keyword in message_lower for keyword in completion_keywords)

    def _generate_response(self, context: InterviewContext, user_message: str, language: str = "en") -> str:
        """Generate a response based on context and user message"""
        # Get responses for the specified language, fallback to English
        allowed_to_proceed = self.guardian_llm.generate() 
        if not allowed_to_proceed:
            return "I'm sorry, I can't allow you to proceed with this interview."
        small_llm_response = self.small_llm.generate()
        final_response = self.judge_llm.generate()
        responses = self.hard_coded_responses.get(language, self.hard_coded_responses["en"])

        # For now, use hard-coded responses in sequence
        response = responses[self.response_index % len(responses)]
        self.response_index += 1

        # Add some context-aware logic for the first message
        if len(context.conversation_history) == 0:
            if language == "he":
                return f"שלום {context.candidate_name}! ברוך הבא לראיון שלך עבור {context.interview_title}. בואו נתחיל עם שאלה פשוטה: אתה יכול לספר לי קצת על עצמך ולמה אתה מעוניין בתפקיד הזה?"
            elif language == "ar":
                return f"مرحباً {context.candidate_name}! أهلاً بك في مقابلتك لمنصب {context.interview_title}. دعنا نبدأ بسؤال بسيط: هل يمكنك أن تخبرني قليلاً عن نفسك ولماذا أنت مهتم بهذا المنصب؟"
            else:
                return f"Hello {context.candidate_name}! Welcome to your interview for {context.interview_title}. Let's start with a simple question: Can you tell me a bit about yourself and why you're interested in this position?"

        # Add some variety based on conversation length
        conversation_length = len(context.conversation_history)
        if conversation_length > 10:
            if language == "he":
                return "תודה על כל התשובות שלך. יש משהו נוסף שאתה רוצה לשתף, או שנסיים את הראיון?"
            elif language == "ar":
                return "شكراً لك على جميع إجاباتك. هل هناك شيء آخر تود مشاركته، أم يجب أن نختتم المقابلة؟"
            else:
                return "Thank you for all your responses. Is there anything else you'd like to share, or shall we conclude the interview?"

        # TODO: In the future, we can use the question objects from context.questions
        # to provide more intelligent responses based on question importance, category, etc.
        # For example:
        # - High importance questions could get more detailed follow-ups
        # - Technical questions could trigger more technical responses
        # - Behavioral questions could ask for specific examples

        return response

    def _generate_completion_response(self, context: InterviewContext, language: str = "en") -> str:
        """Generate a completion response when the interview ends"""
        if language == "he":
            return f"תודה {context.candidate_name} על הזמן שהקדשת להשלמת הראיון הזה. התשובות שלך נרשמו ויבדקו על ידי הצוות שלנו. אנחנו מעריכים את העניין שלך בתפקיד {context.interview_title} ונהיה בקשר בקרוב."
        elif language == "ar":
            return f"شكراً لك {context.candidate_name} على الوقت الذي قضيته في إكمال هذه المقابلة. تم تسجيل إجاباتك وستتم مراجعتها من قبل فريقنا. نحن نقدر اهتمامك بمنصب {context.interview_title} وسنتواصل معك قريباً."
        else:
            return f"Thank you {context.candidate_name} for taking the time to complete this interview. Your responses have been recorded and will be reviewed by our team. We appreciate your interest in the {context.interview_title} position and will be in touch soon."

    def prepare_interview_context(
        self,
        candidate_name: str,
        interview_title: str,
        job_description: Optional[str],
        questions: list["QuestionResponse"],
        conversation_history: list[dict]
    ) -> InterviewContext:
        """Prepare interview context for LLM processing"""
        # Ensure the model is rebuilt to resolve forward references
        try:
            from app.schemas.question import QuestionResponse
            InterviewContext.model_rebuild()
        except Exception:
            pass  # Model might already be rebuilt

        # Convert conversation history to ChatMessage objects
        from datetime import datetime
        chat_messages = []
        for msg in conversation_history:
            timestamp_str = msg.get("timestamp")
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
            chat_messages.append(ChatMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                timestamp=timestamp,
                question_id=msg.get("question_id")
            ))

        return InterviewContext(
            candidate_name=candidate_name,
            interview_title=interview_title,
            job_description=job_description,
            questions=questions,
            conversation_history=chat_messages
        )


# Create instance for dependency injection
interview_llm_service = InterviewLLMService()
