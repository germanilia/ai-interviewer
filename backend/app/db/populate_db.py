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

        # 7. Create Sample Interview Questions with Answers for completed interview
        create_sample_interview_questions(
            db, created_interviews, created_questions)

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



def create_sample_interview_questions(db: Session, interviews: list, questions: list):
    """
    יצירת שאלות ראיון לדוגמה עם תשובות למועמדים שסיימו.
    זה מדגים איך המערכת שומרת תגובות לשאלות וניתוח AI.
    """
    logger.info("יצירת שאלות ראיון לדוגמה עם תשובות...")

    # Find a candidate with completed status
    completed_candidates = db.query(Candidate).filter(
        Candidate.interview_status == "completed"
    ).all()

    if not completed_candidates:
        logger.info("לא נמצאו מועמדים שסיימו, מדלג על יצירת שאלות ראיון")
        return

    # Use the first completed candidate
    completed_candidate = completed_candidates[0]
    if completed_candidate.interview_id is None:
        logger.info("למועמד שסיים אין ראיון שהוקצה")
        return

    # Get the interview for this candidate
    interview = next((i for i in interviews if i.id == completed_candidate.interview_id), None)
    if not interview:
        logger.info("לא ניתן למצוא ראיון למועמד שסיים")
        return

    # Get relevant questions for security guard position
    security_questions = [q for q in questions if q.category in [
        QuestionCategory.CRIMINAL_BACKGROUND,
        QuestionCategory.ETHICS,
        QuestionCategory.TRUSTWORTHINESS
    ]][:5]  # Take first 5 questions

    # Sample answers and AI analysis for the completed interview
    sample_qa_data = [
        {
            "question": next((q for q in security_questions if "עבר פלילי" in q.question_text), security_questions[0]),
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
            "question": next((q for q in security_questions if "גניבה" in q.question_text), security_questions[1]),
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
            "question": next((q for q in security_questions if "פיטורים" in q.question_text or "פוטרת" in q.question_text), security_questions[2]),
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
            "question": next((q for q in security_questions if "סמים" in q.question_text or "חומרים" in q.question_text), security_questions[3]),
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
            "question": next((q for q in security_questions if "אמון" in q.question_text or "אחריות" in q.question_text), security_questions[4] if len(security_questions) > 4 else security_questions[0]),
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
        }
    ]

    # Create interview questions with answers
    for index, qa_data in enumerate(sample_qa_data):
        interview_question = InterviewQuestion(
            interview_id=interview.id,
            question_id=qa_data["question"].id,
            status=InterviewQuestionStatus.ANSWERED,
            order_index=index + 1,
            question_text_snapshot=qa_data["question"].question_text,
            candidate_answer=qa_data["answer"],
            ai_analysis=qa_data["ai_analysis"],
            asked_at=datetime.now() - timedelta(days=5, hours=1),
            answered_at=datetime.now() - timedelta(days=5, hours=1, minutes=2)
        )
        db.add(interview_question)

    db.flush()
    logger.info(f"נוצרו {len(sample_qa_data)} שאלות ראיון עם תשובות")


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
