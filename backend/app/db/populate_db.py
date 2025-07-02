import logging
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.interview import (
    Interview, Question, InterviewQuestion,
    QuestionImportance,
    QuestionCategory, InterviewQuestionStatus
)
from app.models.custom_prompt import CustomPrompt, PromptType
from app.schemas.interview import generate_pass_key
from app.db import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample users to populate the database
SAMPLE_USERS = [
    {
        "username": "admin",
        "email": "admin@midot.com",
        "full_name": "מנהל מערכת",
        "is_active": True,
        "role": UserRole.ADMIN
    },
    {
        "username": "hr_manager",
        "email": "hr@midot.com",
        "full_name": "מנהל משאבי אנוש",
        "is_active": True,
        "role": UserRole.USER
    },
    {
        "username": "recruiter1",
        "email": "recruiter1@midot.com",
        "full_name": "שרה כהן",
        "is_active": True,
        "role": UserRole.USER
    },
    {
        "username": "recruiter2",
        "email": "recruiter2@midot.com",
        "full_name": "מיכה לוי",
        "is_active": True,
        "role": UserRole.USER
    }
]

# Sample candidates to populate the database
SAMPLE_CANDIDATES = [
    {
        "first_name": "יוסף",
        "last_name": "כהן",
        "email": "yosef.cohen@email.com",
        "phone": "+972-54-1234567"
    },
    {
        "first_name": "רחל",
        "last_name": "לוי",
        "email": "rachel.levi@email.com",
        "phone": "+972-52-1234568"
    },
    {
        "first_name": "דוד",
        "last_name": "אברהם",
        "email": "david.abraham@email.com",
        "phone": "+972-53-1234569"
    },
    {
        "first_name": "מרים",
        "last_name": "יוסף",
        "email": "miriam.yosef@email.com",
        "phone": "+972-54-1234570"
    },
    {
        "first_name": "אליעזר",
        "last_name": "גולדברג",
        "email": "eliezer.goldberg@email.com",
        "phone": "+972-52-1234571"
    },
    {
        "first_name": "שרה",
        "last_name": "פרידמן",
        "email": "sarah.friedman@email.com",
        "phone": "+972-53-1234572"
    },
    {
        "first_name": "משה",
        "last_name": "רוזנברג",
        "email": "moshe.rosenberg@email.com",
        "phone": "+972-54-1234573"
    },
    {
        "first_name": "עדה",
        "last_name": "כהן",
        "email": "ada.cohen@email.com",
        "phone": "+972-52-1234574"
    },
    {
        "first_name": "אברהם",
        "last_name": "שוורץ",
        "email": "avraham.schwartz@email.com",
        "phone": "+972-53-1234575"
    },
    {
        "first_name": "רבקה",
        "last_name": "ברק",
        "email": "rivka.barak@email.com",
        "phone": "+972-54-1234576"
    },
    {
        "first_name": "יעקב",
        "last_name": "שפירא",
        "email": "yaakov.shapira@email.com",
        "phone": "+972-52-1234577"
    },
    {
        "first_name": "לאה",
        "last_name": "גרין",
        "email": "lea.green@email.com",
        "phone": "+972-53-1234578"
    },
    {
        "first_name": "שמואל",
        "last_name": "גולד",
        "email": "shmuel.gold@email.com",
        "phone": "+972-54-1234579"
    },
    {
        "first_name": "רות",
        "last_name": "ברגמן",
        "email": "ruth.bergman@email.com",
        "phone": "+972-52-1234580"
    },
    {
        "first_name": "אהרון",
        "last_name": "רוזן",
        "email": "aharon.rosen@email.com",
        "phone": "+972-53-1234581"
    }
]

# Sample jobs to populate the database
SAMPLE_JOBS = [
    {
        "title": "מאבטח",
        "description": "אחראי על שמירת הביטחון והבטיחות במתחם, מעקב אחר ציוד מעקב והבטחת עמידה בפרוטוקולי אבטחה.",
        "department": "אבטחה וביטחון"
    },
    {
        "title": "אנליסט פיננסי",
        "description": "ניתוח נתונים פיננסיים, הכנת דוחות ומתן המלצות לקבלת החלטות השקעה. התפקיד דורש רמה גבוהה של יושרה ואמינות.",
        "department": "כספים"
    },
    {
        "title": "נציג שירות לקוחות",
        "description": "טיפול בפניות לקוחות, פתרון תלונות ושמירה על יחסי לקוחות חיוביים. התפקיד דורש התנהגות אתית ואמינות.",
        "department": "שירות לקוחות"
    },
    {
        "title": "מפקח מחסן",
        "description": "פיקוח על פעילות המחסן, ניהול מלאי והדרכת צוות. התפקיד כולל טיפול בסחורה יקרת ערך ודורש אמינות.",
        "department": "תפעול"
    },
    {
        "title": "גזבר",
        "description": "ניהול כספים, עיבוד תשלומים וטיפול בעסקאות כספיות. התפקיד דורש אמינות מלאה וניהול נכון של נכסים כספיים.",
        "department": "כספים"
    },
    {
        "title": "מנהל פרויקטים",
        "description": "ניהול פרויקטים מורכבים, הנהגת צוותים ודיווח לדירקטוריון. התפקיד דורש יושרה גבוהה ואמינות בניהול משאבים.",
        "department": "ניהול"
    }
]

# Sample questions for integrity interviews based on Midot specifications
SAMPLE_QUESTIONS = [
    # Criminal Background Questions - רקע פלילי
    {
        "title": "גילוי עבר פלילי",
        "question_text": "האם נגדך הוגש אי פעם כתב אישום או הורשעת בעבירה כלשהי, כולל עבירות פליליות וגם עבירות משמעת? אנא ספק מידע מלא וכנה על כל רקע פלילי.",
        "instructions": "שאלה חובה הדורשת תשובה מלאה. בדקו אם התשובה נמנעת או לא מלאה. חפשו סימנים של הימנעות מתשובה.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.CRIMINAL_BACKGROUND
    },
    {
        "title": "בעיות משפטיות תלויות ועומדות",
        "question_text": "האם אתה נתון כרגע לחקירה משטרתית, הליכים משפטיים או חקירות? זה כולל כל תיק משפטי תלוי ועומד או עניינים משפטיים מתמשכים.",
        "instructions": "בדקו פרטים אם מוזכרים נושאים משפטיים. חפשו עקביות בתשובות ותשומת לב למתחמקים.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.CRIMINAL_BACKGROUND
    },
    {
        "title": "האשמות משפטיות",
        "question_text": "האם הואשמת אי פעם בעבירה, גם אם לא הוגש נגדך כתב אישום או לא הורשעת? אנא הסבר כל מצב שבו נחקרת או נחקפת על ידי רשויות החוק.",
        "instructions": "זה עוזר לזהות בעיות פוטנציאליות שלא מכוסות ברישומי הרשעות. המשיכו עם כל אזכור של האשמות.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.CRIMINAL_BACKGROUND
    },
    {
        "title": "מעורבות עם רשויות החוק",
        "question_text": "האם היית מעורב אי פעם במצב שהצריך התערבות משטרה או רשויות אכיפת החוק, גם אם לא הוגשו נגדך האשמות?",
        "instructions": "בדקו את רמת הכנות ונכונות לשתף מידע. זה יכול לחשוף מצבים בעייתיים שלא הגיעו לכתבי אישום.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.CRIMINAL_BACKGROUND
    },

    # Prior Dismissals Questions - פיטורים קודמים
    {
        "title": "היסטוריית פיטורים מעבודה",
        "question_text": "האם פוטרת אי פעם, הופסקה העסקתך או התבקשת להתפטר מעבודה? אם כן, אנא הסבר את הנסיבות ומה למדת מהחוויה.",
        "instructions": "חפשו דפוסים של פיטורים, קבלת אחריות ולקחים שנלמדו. בדקו פרטים על הסיבות.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.DISMISSALS
    },
    {
        "title": "התנהגות בלתי הולמת במקום העבודה",
        "question_text": "האם נוקטו נגדך אי פעם צעדים משמעתיים, הושעית או קיבלת אזהרה בכתב בעבודה על התנהגות בלתי הולמת, הפרת כללים או בעיות ביצועים?",
        "instructions": "העריכו כנות ונכונות לקחת אחריות. חפשו דפוסים של בעיות במקום העבודה.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.DISMISSALS
    },
    {
        "title": "יחסים עם הנהלה וצוות",
        "question_text": "האם היו לך אי פעם קונפליקטים משמעותיים עם מנהלים או עמיתים לעבודה שהובילו לצעדים רשמיים או תלונות?",
        "instructions": "בדקו יכולת עבודה בצוות וניהול קונפליקטים. חפשו דפוסים בקשיים בין-אישיים.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.DISMISSALS
    },

    # Drug Use Questions - שימוש בסמים
    {
        "title": "היסטוריית שימוש בחומרים",
        "question_text": "האם אתה משתמש כרגע או השתמשת בסמים לא חוקיים? אנא היה כנה לגבי ההיסטוריה שלך בשימוש בחומרים, כולל תדירות וסוגי החומרים.",
        "instructions": "העריכו סיכון נוכחי וכנות. המשיכו עם כל הודאה בשאלות על תדירות והשפעה על העבודה.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.DRUG_USE
    },
    {
        "title": "השפעת אלכוהול וחומרים",
        "question_text": "האם שימוש באלכוהול או חומרים השפיע אי פעם על ביצועי העבודה שלך, נוכחות או יחסים מקצועיים? אנא תאר כל אירועים.",
        "instructions": "חפשו השפעה על החיים המקצועיים והערכת סיכון נוכחי.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.DRUG_USE
    },
    {
        "title": "טיפול והתמודדות",
        "question_text": "האם פנית אי פעם לטיפול או עזרה מקצועית בנושא שימוש באלכוהול או סמים? איך אתה מתמודד עם לחצים או מצבי קושי?",
        "instructions": "העריכו נכונות לקבל עזרה ויכולת התמודדות בריאה. זה יכול להצביע על מודעות עצמית חיובית.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.DRUG_USE
    },

    # Ethics and Trustworthiness Questions - אתיקה ואמינות
    {
        "title": "גניבה ואי יושר",
        "question_text": "האם לקחת אי פעם משהו שלא השייך לך ממעסיק, עמית לעבודה או לקוח? זה כולל כסף, סחורה, ציוד או מידע.",
        "instructions": "קריטי לתפקידים עם גישה לחפצי ערך או מידע רגיש. בדקו פרטים ונסיבות.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.ETHICS
    },
    {
        "title": "הונאה והטעיה",
        "question_text": "האם זייפת אי פעם מסמכים, שיקרת בבקשות או התעסקת בכל צורה של הונאה? זה כולל הונאה בקורות חיים, מניפולציה של דפי נוכחות או תביעות הוצאות כוזבות.",
        "instructions": "חיוני להערכת יושרה. חפשו דפוסים של הטעיה וכנות נוכחית.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.ETHICS
    },
    {
        "title": "הפרת סודיות",
        "question_text": "האם שיתפת אי פעם מידע סודי באופן לא מתאים, הפרת מדיניות פרטיות או חשפת מידע רגיש של החברה או לקוחות?",
        "instructions": "חשוב לתפקידים עם גישה לנתונים רגישים. העריכו הבנה של סודיות.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.TRUSTWORTHINESS
    },
    {
        "title": "ניגוד עניינים",
        "question_text": "האם היית אי פעם במצב שבו האינטרסים האישיים שלך היו בסתירה לחובותיך המקצועיות? איך התמודדת עם זה?",
        "instructions": "העריכו קבלת החלטות אתית ושקיפות לגבי קונפליקטים פוטנציאליים.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.ETHICS
    },
    {
        "title": "דיווח על התנהגות בלתי הולמת",
        "question_text": "אם היית עד להתנהגות בלתי הולמת או לא אתית של עמית לעבודה, מה היית עושה? האם היית אי פעם במצב כזה?",
        "instructions": "העריכו נכונות לדווח על התנהגות לא תקינה ותקנים אתיים. בדקו דוגמאות אמיתיות אם מוזכרות.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.ETHICS
    },

    # General Integrity Questions - שאלות יושרה כלליות
    {
        "title": "הערכת יושרה",
        "question_text": "תאר מצב שבו היית צריך לבחור בין עשיית מה שקל לעשיית מה שנכון. מה בחרת ולמה?",
        "instructions": "העריכו חשיבה מוסרית ויושרה בקבלת החלטות. חפשו דוגמאות ספציפיות.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.TRUSTWORTHINESS
    },
    {
        "title": "אתיקה במקום העבודה",
        "question_text": "אם היית רואה עמית לעבודה גונב או מתנהג באופן לא אתי, מה היית עושה? האם היית אי פעם במצב כזה?",
        "instructions": "העריכו נכונות לדווח על התנהגות לא תקינה ותקנים אתיים. בדקו דוגמאות אמיתיות אם מוזכרות.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.ETHICS
    },
    {
        "title": "אמון ואחריות",
        "question_text": "תן דוגמה למצב שבו מישהו בטח בך עם משהו חשוב. איך התמודדת עם האחריות הזו?",
        "instructions": "העריכו הבנה של אמון ואחריות. חפשו דוגמאות קונקרטיות.",
        "importance": QuestionImportance.OPTIONAL,
        "category": QuestionCategory.TRUSTWORTHINESS
    },
    {
        "title": "טעויות וחרטה",
        "question_text": "תאר זמן שבו עשית משהו לא נכון בעבודה או בחיים האישיים. איך התמודדת עם זה ומה למדת?",
        "instructions": "העריכו יכולת לקחת אחריות, להכיר בטעויות וללמוד מהן. חפשו כנות אמיתית.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.TRUSTWORTHINESS
    },
    {
        "title": "לחץ ופיתוי",
        "question_text": "תאר מצב שבו היית תחת לחץ לעשות משהו שידעת שהוא לא נכון. איך התמודדת עם המצב?",
        "instructions": "העריכו עמידות בפני לחץ ונכונות לעמוד על עקרונות אתיים גם במצבים קשים.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.ETHICS
    },

    # Workplace Behavior Questions - התנהגות במקום העבודה
    {
        "title": "עבודת צוות ושיתוף פעולה",
        "question_text": "איך אתה מתמודד עם מצבים שבהם אתה לא מסכים עם החלטות של הנהלה או עמיתים לעבודה?",
        "instructions": "העריכו יכולת עבודה בצוות, התמודדות עם קונפליקטים ושמירה על מקצועיות.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.TRUSTWORTHINESS
    },
    {
        "title": "אמינות ועמידה בזמנים",
        "question_text": "איך אתה מבטיח שתעמוד בהתחייבויות ודדליינים? האם היו מצבים שבהם לא עמדת בהתחייבות?",
        "instructions": "העריכו אמינות, ניהול זמן ונכונות להתחייב. חפשו דוגמאות לטיפול באתגרים.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.TRUSTWORTHINESS
    }
]

# Default prompts to populate the database
DEFAULT_PROMPTS = [
    {
        "prompt_type": PromptType.EVALUATION,
        "name": "Default Evaluation Prompt",
        "content": """
Your task is to generate appropriate interview responses based on the conversation context and current question.

Guidelines:
1. Generate natural, conversational responses that guide the interview forward
2. Ask follow-up questions when appropriate
3. Maintain a professional but friendly tone
4. Focus on the current question while considering the overall interview context
5. Encourage detailed responses from candidates

Response format:
- reasoning: Your analysis of the conversation and response strategy
- response: The actual response to send to the candidate
- was_question_answered: Whether the current question was sufficiently answered
- answered_question_index: Index of the question that was answered (if applicable)
""",
        "description": "Default prompt for initial response generation using evaluation model",
        "is_active": True
    },
    {
        "prompt_type": PromptType.JUDGE,
        "name": "Default Judge Prompt",
        "content": """
Your task is to evaluate and refine interview responses for final delivery.

Guidelines:
1. Review the initial response for appropriateness and effectiveness
2. Ensure the response maintains interview flow and professionalism
3. Verify that sensitive topics are handled appropriately
4. Refine language for clarity and engagement
5. Ensure responses align with interview objectives

Response format:
- reasoning: Your evaluation of the initial response and refinement strategy
- response: The final refined response to send to the candidate
- was_question_answered: Whether the current question was sufficiently answered
- answered_question_index: Index of the question that was answered (if applicable)
""",
        "description": "Default prompt for final response evaluation and refinement using judge model",
        "is_active": True
    },
    {
        "prompt_type": PromptType.GUARDRAILS,
        "name": "Default Guardrails Prompt",
        "content": """
Your task is to evaluate whether this conversation can continue safely and professionally.

Check for:
1. Inappropriate language or content
2. Discriminatory statements
3. Harassment or offensive behavior
4. Off-topic discussions that are unprofessional
5. Attempts to manipulate or exploit the system
6. Personal attacks or hostile behavior
7. Sharing of sensitive personal information inappropriately

Guidelines:
- Be permissive for normal interview discussions
- Allow candidates to discuss their experiences, even if they mention challenges
- Only flag truly inappropriate or harmful content
- Consider cultural differences in communication styles
- Focus on professional interview context
- Allow reasonable personal anecdotes related to work experience

Very important you are not allowed to disqualify candidates if you find them unfit for the job,
the only purpose of this evaluation is to check if the conversation is still related to the interview or was steered to a different topic.

Dont consider ethical and moral issues as reason not. to continue, it doesn't event matter, you need to filter spam and mis use of the system to any other task than the interview.
""",
        "description": "Default prompt for content safety and appropriateness checking",
        "is_active": True
    },
    {
        "prompt_type": PromptType.QUESTION_EVALUATION,
        "name": "Default Question Evaluation Prompt",
        "content": """
Your task:
1. Analyze the conversation history to determine if the candidate has provided a complete and satisfactory answer to the current question
2. Consider the depth, relevance, and completeness of the candidate's response
3. A question is "fully answered" if the candidate has addressed the core aspects of what was being asked
4. Partial answers, evasive responses, or off-topic responses should be considered as NOT fully answered

Please provide your evaluation in the following format:
- reasoning: Your detailed analysis of why the question was or wasn't fully answered
- question_fully_answered: true if the question was completely answered, false otherwise

Be strict in your evaluation - only mark as fully answered if the candidate genuinely addressed the question comprehensively.
""",
        "description": "Default prompt for evaluating if interview questions were answered",
        "is_active": True
    }
]


def get_default_initial_greeting(language: str) -> str:
    """Get default initial greeting based on language"""
    if language == "Hebrew":
        return "שלום {candidate_name}, ברוך הבא לראיון שלך עבור תפקיד {interview_title}. איך אתה מרגיש היום?"
    elif language == "Arabic":
        return "مرحباً {candidate_name}، أهلاً بك في مقابلتك لمنصب {interview_title}. كيف تشعر اليوم؟"
    else:  # English
        return "Hello {candidate_name}, welcome to your interview for the {interview_title} position. How are you feeling today?"


def populate_db():
    """
    מילוי מסד הנתונים בנתונים לדוגמה עבור מערכת ראיון יושרה של צ'אטבוט AI.
    זה כולל משתמשים, מועמדים, עבודות, שאלות וראיונות לדוגמה.
    """
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info(
                f"מסד הנתונים כבר מכיל {existing_users} משתמשים. מדלג על מילוי.")
            return True

        logger.info("מתחיל מילוי מסד הנתונים בנתונים לדוגמה...")

        # 1. Create Users first (needed for foreign keys)
        logger.info("יצירת משתמשים לדוגמה...")
        created_users = []
        for user_data in SAMPLE_USERS:
            user = User(**user_data)
            db.add(user)
            created_users.append(user)

        db.flush()  # Flush to get IDs without committing
        db.refresh(created_users[0])  # Refresh to get the ID
        admin_user = created_users[0]  # First user is admin
        logger.info(
            f"נוצרו {len(created_users)} משתמשים, admin_user.id = {admin_user.id}")

        # 2. Create Interviews with Job Information
        logger.info("יצירת ראיונות לדוגמה...")
        created_interviews = []
        for job_data in SAMPLE_JOBS:
            interview = Interview(
                job_title=job_data["title"],
                job_description=job_data["description"],
                job_department=job_data["department"],
                language="Hebrew",  # Default to Hebrew
                initial_greeting=get_default_initial_greeting("Hebrew"),
                created_by_user_id=admin_user.id
            )
            db.add(interview)
            created_interviews.append(interview)

        db.flush()
        logger.info(f"נוצרו {len(created_interviews)} ראיונות")

        # 3. Create Candidates and assign them to interviews
        logger.info("יצירת מועמדים לדוגמה...")
        created_candidates = []
        for i, candidate_data in enumerate(SAMPLE_CANDIDATES):
            # Assign candidates to interviews in round-robin fashion
            interview = created_interviews[i % len(created_interviews)]
            candidate = Candidate(
                first_name=candidate_data["first_name"],
                last_name=candidate_data["last_name"],
                email=candidate_data["email"],
                phone=candidate_data["phone"],
                interview_id=interview.id,
                pass_key=generate_pass_key(),
                created_by_user_id=admin_user.id
            )
            db.add(candidate)
            created_candidates.append(candidate)

        db.flush()
        logger.info(f"נוצרו {len(created_candidates)} מועמדים")

        # 4. Create Questions
        logger.info("יצירת שאלות לדוגמה...")
        created_questions = []
        for question_data in SAMPLE_QUESTIONS:
            question = Question(
                title=question_data["title"],
                question_text=question_data["question_text"],
                instructions=question_data["instructions"],
                importance=question_data["importance"],
                category=question_data["category"],
                created_by_user_id=admin_user.id
            )
            db.add(question)
            created_questions.append(question)

        db.flush()
        logger.info(f"נוצרו {len(created_questions)} שאלות")

        # 5. Update candidates with sample interview data
        create_sample_interview_data(
            db, created_candidates, created_questions, admin_user)

        # 6. Assign questions to interviews (2 from each category)
        assign_questions_to_interviews(db, created_interviews, created_questions)

        # 7. Create Sample Interview Questions with Answers for completed interview
        create_sample_interview_questions(
            db, created_interviews, created_questions)

        # 8. Create Default Custom Prompts
        logger.info("יצירת הנחיות ברירת מחדל...")
        populate_default_prompts(db, admin_user)

        db.commit()
        logger.info("מסד הנתונים מולא בהצלחה עם כל הנתונים לדוגמה!")
        logger.info(f"סיכום: {len(created_users)} משתמשים, {len(created_candidates)} מועמדים, {len(created_questions)} שאלות, "
                    f"{len(created_interviews)} ראיונות")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"שגיאה במילוי מסד הנתונים: {e}")
        return False
    finally:
        db.close()

    return True


def populate_default_prompts(db: Session, admin_user: User):
    """
    יצירת הנחיות ברירת מחדל במסד הנתונים.
    """
    logger.info("יצירת הנחיות ברירת מחדל...")

    created_prompts = []
    for prompt_data in DEFAULT_PROMPTS:
        # Check if a prompt of this type already exists
        existing_prompt = db.query(CustomPrompt).filter(
            CustomPrompt.prompt_type == prompt_data["prompt_type"],
            CustomPrompt.is_active == True
        ).first()

        if not existing_prompt:
            prompt = CustomPrompt(
                prompt_type=prompt_data["prompt_type"],
                name=prompt_data["name"],
                content=prompt_data["content"],
                description=prompt_data["description"],
                is_active=prompt_data["is_active"],
                created_by_user_id=admin_user.id
            )
            db.add(prompt)
            created_prompts.append(prompt)
            logger.info(f"נוצרה הנחיה ברירת מחדל: {prompt_data['name']}")
        else:
            logger.info(f"הנחיה מסוג {prompt_data['prompt_type']} כבר קיימת, מדלג")

    db.flush()
    logger.info(f"נוצרו {len(created_prompts)} הנחיות ברירת מחדל")


def create_sample_interview_data(db: Session, candidates: list, questions: list, admin_user: User):
    """
    עדכון מועמדים לדוגמה עם נתוני ראיון ספציפיים.
    """
    logger.info("יצירת נתוני ראיון לדוגמה עבור מועמדים...")

    # Update some candidates with sample interview data
    if len(candidates) > 0:
        # Update first candidate with completed interview data
        candidates[0].interview_status = "completed"
        candidates[0].score = 85
        candidates[0].integrity_score = "high"
        candidates[0].risk_level = "low"
        candidates[0].interview_date = datetime.now() - timedelta(days=5)
        candidates[0].completed_at = datetime.now() - timedelta(days=5)
        candidates[0].report_summary = "המועמד הפגין יושרה גבוהה לאורך כל הראיון."
        candidates[0].analysis_notes = "מומלץ להעסקה. פרופיל יושרה חזק."

    if len(candidates) > 1:
        # Update second candidate with in-progress interview
        candidates[1].interview_status = "in_progress"
        candidates[1].interview_date = datetime.now()

    if len(candidates) > 2:
        # Update third candidate with pending interview
        candidates[2].interview_status = "pending"
        candidates[2].interview_date = datetime.now() + timedelta(days=2)

    db.flush()
    logger.info("עודכנו מועמדים עם נתוני ראיון לדוגמה")


def assign_questions_to_interviews(db: Session, interviews: list, questions: list):
    """
    הקצאת שאלות לראיונות - 2 שאלות מכל קטגוריה לכל ראיון.
    זה מבטיח שכל ראיון מכסה את כל התחומים הנדרשים.
    """
    logger.info("מקצה שאלות לראיונות - 2 מכל קטגוריה...")
    
    # Group questions by category
    questions_by_category = {}
    for question in questions:
        if question.category not in questions_by_category:
            questions_by_category[question.category] = []
        questions_by_category[question.category].append(question)
    
    # Log available categories and question counts
    for category, category_questions in questions_by_category.items():
        logger.info(f"קטגוריה {category}: {len(category_questions)} שאלות")
    
    # Assign questions to each interview
    for interview in interviews:
        interview_questions = []
        order_index = 1
        
        # For each category, assign 2 questions
        for category, category_questions in questions_by_category.items():
            # Take up to 2 questions from this category
            questions_to_assign = category_questions[:2]
            
            for question in questions_to_assign:
                interview_question = InterviewQuestion(
                    interview_id=interview.id,
                    question_id=question.id,
                    status=InterviewQuestionStatus.PENDING,
                    order_index=order_index,
                    question_text_snapshot=question.question_text
                )
                db.add(interview_question)
                interview_questions.append(interview_question)
                order_index += 1
        
        logger.info(f"הוקצו {len(interview_questions)} שאלות לראיון '{interview.job_title}'")
    
    db.flush()
    logger.info("הקצאת שאלות לראיונות הושלמה")


def create_sample_interview_questions(db: Session, interviews: list, questions: list):
    """
    עדכון שאלות ראיון קיימות עם תשובות למועמדים שסיימו.
    זה מדגים איך המערכת שומרת תגובות לשאלות וניתוח AI.
    """
    logger.info("עדכון שאלות ראיון קיימות עם תשובות לדוגמה...")

    # Find a candidate with completed status
    completed_candidates = db.query(Candidate).filter(
        Candidate.interview_status == "completed"
    ).all()

    if not completed_candidates:
        logger.info("לא נמצאו מועמדים שסיימו, מדלג על עדכון שאלות ראיון")
        return

    # Use the first completed candidate
    completed_candidate = completed_candidates[0]
    if completed_candidate.interview_id is None:
        logger.info("למועמד שסיים אין ראיון שהוקצה")
        return

    # Get existing interview questions for this interview
    existing_interview_questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == completed_candidate.interview_id
    ).order_by(InterviewQuestion.order_index).all()

    if not existing_interview_questions:
        logger.info("לא נמצאו שאלות ראיון קיימות עבור המועמד שסיים")
        return

    # Sample answers by category for realistic responses
    sample_answers_by_category = {
        QuestionCategory.CRIMINAL_BACKGROUND: [
            {
                "answer": "לא, אף פעם לא הורשעתי בעבירה כלשהי. יש לי רקע פלילי נקי ללא מעצרים או האשמות.",
                "ai_analysis": {
                    "sentiment": "confident",
                    "honesty_score": 0.95,
                    "completeness": 0.9,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low"
                }
            },
            {
                "answer": "לא, אף פעם לא הייתי מעורב במצב שדרש התערבות משטרה. אני מנסה להימנע מצרות ולחיות חיים נקיים.",
                "ai_analysis": {
                    "sentiment": "clear",
                    "honesty_score": 0.92,
                    "completeness": 0.88,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low"
                }
            }
        ],
        QuestionCategory.DRUG_USE: [
            {
                "answer": "לא, אני לא משתמש בסמים לא חוקיים ולא השתמשתי בעבר. אני שותה אלכוהול באירועים חברתיים בלבד ובכמויות מתונות.",
                "ai_analysis": {
                    "sentiment": "clear",
                    "honesty_score": 0.93,
                    "completeness": 0.95,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low"
                }
            },
            {
                "answer": "אני מעולם לא נטלתי עזרה מקצועית כי לא הייתי צריך. אני מתמודד עם לחץ באמצעות ספורט ומדיטציה.",
                "ai_analysis": {
                    "sentiment": "confident",
                    "honesty_score": 0.89,
                    "completeness": 0.85,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low"
                }
            }
        ],
        QuestionCategory.ETHICS: [
            {
                "answer": "לא, אף פעם לא לקחתי משהו שלא השייך לי. אני מאמין חזק ביושרה ואמינות.",
                "ai_analysis": {
                    "sentiment": "confident",
                    "honesty_score": 0.92,
                    "completeness": 0.85,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low"
                }
            },
            {
                "answer": "כשראיתי עמית לוקח ציוד משרדי הביתה, דיברתי איתו ישירות והוא החזיר הכל. לא הייתי צריך לדווח למנהל.",
                "ai_analysis": {
                    "sentiment": "responsible",
                    "honesty_score": 0.94,
                    "completeness": 0.92,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low",
                    "notes": "טיפול ישיר ואפקטיבי בבעיה אתית"
                }
            }
        ],
        QuestionCategory.DISMISSALS: [
            {
                "answer": "פוטרתי מעבודה אחת לפני כשלוש שנים בגלל צמצומים בחברה. זה לא היה קשור לביצועים - הם ביטלו את כל המחלקה שלי. קיבלתי מכתב המלצה טוב.",
                "ai_analysis": {
                    "sentiment": "honest",
                    "honesty_score": 0.88,
                    "completeness": 0.9,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low",
                    "notes": "גילוי כנה של איבוד עבודה עקב צמצומים, לא התנהגות לא תקינה"
                }
            },
            {
                "answer": "לא, מעולם לא נוקטו נגדי צעדים משמעתיים. אני מקפיד על כללי החברה ועל התנהגות מקצועית.",
                "ai_analysis": {
                    "sentiment": "confident",
                    "honesty_score": 0.91,
                    "completeness": 0.87,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low"
                }
            }
        ],
        QuestionCategory.TRUSTWORTHINESS: [
            {
                "answer": "בעבודה הקודמת שלי הייתי אחראי על כספי הקופה. המנהל בטח בי עם סכומים גדולים מדי יום. תמיד דאגתי לספור בדיוק ולתעד הכל כראוי, ומעולם לא היה חסר אפילו שקל אחד.",
                "ai_analysis": {
                    "sentiment": "proud",
                    "honesty_score": 0.94,
                    "completeness": 0.92,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low",
                    "notes": "דוגמה קונקרטית של טיפול אחראי בכספים"
                }
            },
            {
                "answer": "אני תמיד מגיע בזמן לעבודה ועומד בכל המועדים. אם אני חושש שלא אעמוד במועד, אני מדווח מראש ומבקש עזרה או הארכה.",
                "ai_analysis": {
                    "sentiment": "responsible",
                    "honesty_score": 0.90,
                    "completeness": 0.88,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low"
                }
            }
        ],
        QuestionCategory.GENERAL: [
            {
                "answer": "בפעם שקבלתי עודף כסף בקופה, החזרתי מיד למנהל גם שזה היה סכום קטן. עשיית הדבר הנכון חשובה לי יותר מכסף.",
                "ai_analysis": {
                    "sentiment": "principled",
                    "honesty_score": 0.96,
                    "completeness": 0.93,
                    "red_flags": [],
                    "follow_up_needed": False,
                    "risk_assessment": "low",
                    "notes": "הפגנה מעולה של יושרה בפעולה"
                }
            }
        ]
    }

    # Update existing interview questions with answers
    updated_count = 0
    category_counters = {}
    
    for interview_question in existing_interview_questions:
        # Get the question to determine its category
        question = next((q for q in questions if q.id == interview_question.question_id), None)
        if not question:
            continue
            
        category = question.category
        if category not in category_counters:
            category_counters[category] = 0
            
        # Get sample answer for this category
        if category in sample_answers_by_category:
            answers_for_category = sample_answers_by_category[category]
            answer_index = category_counters[category] % len(answers_for_category)
            sample_data = answers_for_category[answer_index]
            
            # Update the interview question with answer
            setattr(interview_question, 'status', InterviewQuestionStatus.ANSWERED)
            setattr(interview_question, 'candidate_answer', sample_data["answer"])
            setattr(interview_question, 'ai_analysis', sample_data["ai_analysis"])
            setattr(interview_question, 'asked_at', datetime.now() - timedelta(days=5, hours=1))
            setattr(interview_question, 'answered_at', datetime.now() - timedelta(days=5, hours=1, minutes=2))
            
            category_counters[category] += 1
            updated_count += 1

    db.flush()
    logger.info(f"עודכנו {updated_count} שאלות ראיון עם תשובות לדוגמה")


if __name__ == "__main__":
    # This allows the script to be run directly
    from app.db.init_db import init_db

    # Initialize the database first
    if not init_db():
        logger.error("נכשל לאתחל מסד הנתונים")
        sys.exit(1)

    # Then populate it
    if not populate_db():
        logger.error("נכשל למלא מסד הנתונים")
        sys.exit(1)

    logger.info("מסד הנתונים מולא בהצלחה!")
    sys.exit(0)
