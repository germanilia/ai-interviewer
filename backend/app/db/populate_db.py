import logging
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.interview import (
    Interview, Question, Job, JobQuestion, InterviewQuestion,
    InterviewStatus, IntegrityScore, RiskLevel, QuestionImportance,
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
        "full_name": "System Administrator",
        "is_active": True,
        "role": UserRole.ADMIN
    },
    {
        "username": "hr_manager",
        "email": "hr@midot.com",
        "full_name": "HR Manager",
        "is_active": True,
        "role": UserRole.USER
    },
    {
        "username": "recruiter1",
        "email": "recruiter1@midot.com",
        "full_name": "Sarah Johnson",
        "is_active": True,
        "role": UserRole.USER
    },
    {
        "username": "recruiter2",
        "email": "recruiter2@midot.com",
        "full_name": "Mike Davis",
        "is_active": True,
        "role": UserRole.USER
    }
]

# Sample candidates to populate the database
SAMPLE_CANDIDATES = [
    {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101"
    },
    {
        "first_name": "Emily",
        "last_name": "Johnson",
        "email": "emily.johnson@email.com",
        "phone": "+1-555-0102"
    },
    {
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael.brown@email.com",
        "phone": "+1-555-0103"
    },
    {
        "first_name": "Sarah",
        "last_name": "Davis",
        "email": "sarah.davis@email.com",
        "phone": "+1-555-0104"
    },
    {
        "first_name": "David",
        "last_name": "Wilson",
        "email": "david.wilson@email.com",
        "phone": "+1-555-0105"
    }
]

# Sample jobs to populate the database
SAMPLE_JOBS = [
    {
        "title": "Security Guard",
        "description": "Responsible for maintaining security and safety of premises, monitoring surveillance equipment, and ensuring compliance with security protocols.",
        "department": "Security"
    },
    {
        "title": "Financial Analyst",
        "description": "Analyze financial data, prepare reports, and provide recommendations for investment decisions. Requires high level of integrity and trustworthiness.",
        "department": "Finance"
    },
    {
        "title": "Customer Service Representative",
        "description": "Handle customer inquiries, resolve complaints, and maintain positive customer relationships. Position requires ethical conduct and reliability.",
        "department": "Customer Service"
    },
    {
        "title": "Warehouse Supervisor",
        "description": "Oversee warehouse operations, manage inventory, and supervise staff. Position involves handling valuable merchandise and requires trustworthiness.",
        "department": "Operations"
    }
]

# Sample questions for integrity interviews based on Midot specifications
SAMPLE_QUESTIONS = [
    # Criminal Background Questions
    {
        "title": "Criminal History Disclosure",
        "question_text": "Have you ever been convicted of a crime, including misdemeanors and felonies? Please provide complete and honest information about any criminal history.",
        "instructions": "This question is mandatory and requires a complete answer. Follow up if the response seems evasive or incomplete.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.CRIMINAL_BACKGROUND
    },
    {
        "title": "Pending Legal Issues",
        "question_text": "Are you currently facing any criminal charges, legal proceedings, or investigations? This includes any pending court cases or ongoing legal matters.",
        "instructions": "Probe for details if any legal issues are mentioned. Look for consistency in responses.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.CRIMINAL_BACKGROUND
    },
    {
        "title": "Legal Accusations",
        "question_text": "Have you ever been accused of a crime, even if charges were not filed or you were not convicted? Please explain any situations where you were investigated or questioned by law enforcement.",
        "instructions": "This helps identify potential issues not covered by conviction records. Follow up on any mentions of accusations.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.CRIMINAL_BACKGROUND
    },

    # Prior Dismissals Questions
    {
        "title": "Employment Termination History",
        "question_text": "Have you ever been fired, terminated, or asked to resign from a job? If yes, please explain the circumstances and what you learned from the experience.",
        "instructions": "Look for patterns of termination, responsibility acceptance, and lessons learned. Probe for details about the reasons.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.DISMISSALS
    },
    {
        "title": "Workplace Misconduct",
        "question_text": "Have you ever been disciplined, suspended, or written up at work for misconduct, policy violations, or performance issues? Please describe any formal disciplinary actions.",
        "instructions": "Assess honesty and willingness to take responsibility. Look for patterns of workplace issues.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.DISMISSALS
    },

    # Drug Use Questions
    {
        "title": "Substance Use History",
        "question_text": "Do you currently use or have you used illegal drugs? Please be honest about your substance use history, including frequency and types of substances.",
        "instructions": "Assess current risk and honesty. Follow up on any admissions with questions about frequency and impact on work.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.DRUG_USE
    },
    {
        "title": "Alcohol and Substance Impact",
        "question_text": "Has alcohol or substance use ever affected your work performance, attendance, or professional relationships? Please describe any incidents.",
        "instructions": "Look for impact on professional life and current risk assessment.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.DRUG_USE
    },

    # Ethics and Trustworthiness Questions
    {
        "title": "Theft and Dishonesty",
        "question_text": "Have you ever taken something that didn't belong to you from an employer, coworker, or customer? This includes money, merchandise, supplies, or information.",
        "instructions": "Critical for positions involving access to valuables or sensitive information. Probe for details and circumstances.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.ETHICS
    },
    {
        "title": "Fraud and Deception",
        "question_text": "Have you ever falsified documents, lied on applications, or engaged in any form of fraud? This includes resume fraud, timesheet manipulation, or false expense claims.",
        "instructions": "Essential for assessing integrity. Look for patterns of deception and current honesty.",
        "importance": QuestionImportance.MANDATORY,
        "category": QuestionCategory.ETHICS
    },
    {
        "title": "Confidentiality Breaches",
        "question_text": "Have you ever shared confidential information inappropriately, violated privacy policies, or disclosed sensitive company or customer information?",
        "instructions": "Important for positions with access to sensitive data. Assess understanding of confidentiality.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.TRUSTWORTHINESS
    },
    {
        "title": "Conflict of Interest",
        "question_text": "Have you ever been in a situation where your personal interests conflicted with your professional duties? How did you handle it?",
        "instructions": "Assess ethical decision-making and transparency about potential conflicts.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.ETHICS
    },

    # General Integrity Questions
    {
        "title": "Honesty Assessment",
        "question_text": "Describe a situation where you had to choose between doing what was easy and doing what was right. What did you choose and why?",
        "instructions": "Assess moral reasoning and integrity in decision-making. Look for specific examples.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.TRUSTWORTHINESS
    },
    {
        "title": "Workplace Ethics",
        "question_text": "If you witnessed a coworker stealing or engaging in unethical behavior, what would you do? Have you ever been in such a situation?",
        "instructions": "Assess willingness to report misconduct and ethical standards. Probe for real examples if mentioned.",
        "importance": QuestionImportance.ASK_ONCE,
        "category": QuestionCategory.ETHICS
    },
    {
        "title": "Trust and Reliability",
        "question_text": "Can you provide an example of when someone trusted you with something important? How did you handle that responsibility?",
        "instructions": "Assess understanding of trust and responsibility. Look for concrete examples.",
        "importance": QuestionImportance.OPTIONAL,
        "category": QuestionCategory.TRUSTWORTHINESS
    }
]


def populate_db():
    """
    Populate the database with sample data for the AI Chatbot Integrity Interview system.
    This includes users, candidates, jobs, questions, and sample interviews.
    """
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info(f"Database already contains {existing_users} users. Skipping population.")
            return True

        logger.info("Starting database population with sample data...")

        # 1. Create Users first (needed for foreign keys)
        logger.info("Creating sample users...")
        created_users = []
        for user_data in SAMPLE_USERS:
            user = User(**user_data)
            db.add(user)
            created_users.append(user)

        db.flush()  # Flush to get IDs without committing
        db.refresh(created_users[0])  # Refresh to get the ID
        admin_user = created_users[0]  # First user is admin
        logger.info(f"Created {len(created_users)} users, admin_user.id = {admin_user.id}")

        # 2. Create Candidates
        logger.info("Creating sample candidates...")
        created_candidates = []
        for candidate_data in SAMPLE_CANDIDATES:
            candidate = Candidate(
                first_name=candidate_data["first_name"],
                last_name=candidate_data["last_name"],
                email=candidate_data["email"],
                phone=candidate_data["phone"],
                created_by_user_id=admin_user.id
            )
            db.add(candidate)
            created_candidates.append(candidate)

        db.flush()
        logger.info(f"Created {len(created_candidates)} candidates")

        # 3. Create Jobs
        logger.info("Creating sample jobs...")
        created_jobs = []
        for job_data in SAMPLE_JOBS:
            job = Job(
                title=job_data["title"],
                description=job_data["description"],
                department=job_data["department"],
                created_by_user_id=admin_user.id
            )
            db.add(job)
            created_jobs.append(job)

        db.flush()
        logger.info(f"Created {len(created_jobs)} jobs")

        # 4. Create Questions
        logger.info("Creating sample questions...")
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
        logger.info(f"Created {len(created_questions)} questions")

        # 5. Create Job Question Templates
        create_job_question_templates(db, created_jobs, created_questions)

        # 6. Create Sample Interviews
        created_interviews = create_sample_interviews(db, created_candidates, created_jobs, admin_user)

        # 7. Create Sample Interview Questions with Answers for completed interview
        create_sample_interview_questions(db, created_interviews, created_questions)

        db.commit()
        logger.info("Successfully populated database with all sample data!")
        logger.info(f"Summary: {len(created_users)} users, {len(created_candidates)} candidates, "
                   f"{len(created_jobs)} jobs, {len(created_questions)} questions, "
                   f"{len(created_interviews)} interviews")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error populating database: {e}")
        return False
    finally:
        db.close()

    return True


def create_job_question_templates(db: Session, jobs: list, questions: list):
    """
    Create question templates for each job position.
    This defines which questions should be asked for each job type.
    """
    logger.info("Creating job question templates...")

    # Define question sets for different job types
    security_questions = [q for q in questions if q.category in [
        QuestionCategory.CRIMINAL_BACKGROUND,
        QuestionCategory.ETHICS,
        QuestionCategory.TRUSTWORTHINESS
    ]]

    finance_questions = [q for q in questions if q.category in [
        QuestionCategory.CRIMINAL_BACKGROUND,
        QuestionCategory.ETHICS,
        QuestionCategory.TRUSTWORTHINESS,
        QuestionCategory.DISMISSALS
    ]]

    customer_service_questions = [q for q in questions if q.category in [
        QuestionCategory.ETHICS,
        QuestionCategory.TRUSTWORTHINESS,
        QuestionCategory.DISMISSALS,
        QuestionCategory.DRUG_USE
    ]]

    warehouse_questions = [q for q in questions if q.category in [
        QuestionCategory.CRIMINAL_BACKGROUND,
        QuestionCategory.ETHICS,
        QuestionCategory.DRUG_USE,
        QuestionCategory.TRUSTWORTHINESS
    ]]

    # Map jobs to their question sets
    job_question_mapping = {
        "Security Guard": security_questions,
        "Financial Analyst": finance_questions,
        "Customer Service Representative": customer_service_questions,
        "Warehouse Supervisor": warehouse_questions
    }

    # Create job question relationships
    for job in jobs:
        if job.title in job_question_mapping:
            questions_for_job = job_question_mapping[job.title]
            for index, question in enumerate(questions_for_job):
                job_question = JobQuestion(
                    job_id=job.id,
                    question_id=question.id,
                    order_index=index + 1
                )
                db.add(job_question)

    db.flush()
    logger.info("Created job question templates for all positions")


def create_sample_interviews(db: Session, candidates: list, jobs: list, admin_user: User):
    """
    Create some sample interviews in different states to demonstrate the system.
    """
    logger.info("Creating sample interviews...")

    # Create interviews in different states
    sample_interviews = [
        {
            "candidate": candidates[0],  # John Smith
            "job": jobs[0],  # Security Guard
            "status": InterviewStatus.COMPLETED,
            "score": 85,
            "integrity_score": IntegrityScore.HIGH,
            "risk_level": RiskLevel.LOW,
            "interview_date": datetime.now() - timedelta(days=5),
            "completed_at": datetime.now() - timedelta(days=5),
            "report_summary": "Candidate demonstrated high integrity throughout the interview. No criminal history, honest about minor workplace issues, and showed strong ethical reasoning.",
            "risk_indicators": [],
            "key_concerns": [],
            "analysis_notes": "Recommended for hire. Strong integrity profile with no significant concerns."
        },
        {
            "candidate": candidates[1],  # Emily Johnson
            "job": jobs[1],  # Financial Analyst
            "status": InterviewStatus.IN_PROGRESS,
            "interview_date": datetime.now(),
            "report_summary": None,
            "risk_indicators": None,
            "key_concerns": None,
            "analysis_notes": None
        },
        {
            "candidate": candidates[2],  # Michael Brown
            "job": jobs[2],  # Customer Service Representative
            "status": InterviewStatus.PENDING,
            "interview_date": datetime.now() + timedelta(days=2),
            "report_summary": None,
            "risk_indicators": None,
            "key_concerns": None,
            "analysis_notes": None
        }
    ]

    created_interviews = []
    for interview_data in sample_interviews:
        interview = Interview(
            candidate_id=interview_data["candidate"].id,
            job_id=interview_data["job"].id,
            status=interview_data["status"],
            interview_date=interview_data["interview_date"],
            pass_key=generate_pass_key(),
            score=interview_data.get("score"),
            integrity_score=interview_data.get("integrity_score"),
            risk_level=interview_data.get("risk_level"),
            completed_at=interview_data.get("completed_at"),
            report_summary=interview_data.get("report_summary"),
            risk_indicators=interview_data.get("risk_indicators"),
            key_concerns=interview_data.get("key_concerns"),
            analysis_notes=interview_data.get("analysis_notes"),
            created_by_user_id=admin_user.id
        )
        db.add(interview)
        created_interviews.append(interview)

    db.flush()
    logger.info(f"Created {len(created_interviews)} sample interviews")
    return created_interviews


def create_sample_interview_questions(db: Session, interviews: list, questions: list):
    """
    Create sample interview questions with answers for the completed interview.
    This demonstrates how the system stores question responses and AI analysis.
    """
    logger.info("Creating sample interview questions with answers...")

    # Find the completed interview (John Smith - Security Guard)
    completed_interview = next((i for i in interviews if i.status == InterviewStatus.COMPLETED), None)
    if not completed_interview:
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
            "question": next((q for q in security_questions if "criminal history" in q.question_text.lower()), security_questions[0]),
            "answer": "No, I have never been convicted of any crime. I have a clean criminal record with no arrests or charges.",
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
            "question": next((q for q in security_questions if "theft" in q.question_text.lower()), security_questions[1]),
            "answer": "No, I have never taken anything that didn't belong to me. I believe strongly in honesty and integrity.",
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
            "question": next((q for q in security_questions if "termination" in q.question_text.lower() or "fired" in q.question_text.lower()), security_questions[2]),
            "answer": "I was let go from one job about three years ago due to company downsizing. It wasn't performance related - they eliminated my entire department. I received a good reference letter.",
            "ai_analysis": {
                "sentiment": "honest",
                "honesty_score": 0.88,
                "completeness": 0.9,
                "red_flags": [],
                "follow_up_needed": False,
                "risk_assessment": "low",
                "notes": "Honest disclosure of job loss due to downsizing, not misconduct"
            }
        }
    ]

    # Create interview questions with answers
    for index, qa_data in enumerate(sample_qa_data):
        interview_question = InterviewQuestion(
            interview_id=completed_interview.id,
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
    logger.info(f"Created {len(sample_qa_data)} interview questions with answers")


if __name__ == "__main__":
    # This allows the script to be run directly
    from app.db.init_db import init_db

    # Initialize the database first
    if not init_db():
        logger.error("Failed to initialize database")
        sys.exit(1)

    # Then populate it
    if not populate_db():
        logger.error("Failed to populate database")
        sys.exit(1)

    logger.info("Database populated successfully!")
    sys.exit(0)
