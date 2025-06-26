"""
Test to simulate the exact issue where interview session current_question_index
is not being updated properly between iterations.
"""
from app.crud.interview_session import InterviewSessionDAO
from app.schemas.interview_session import InterviewSessionCreate, InterviewSessionUpdate
from app.models.interview_session import InterviewSessionStatus


def test_session_progression_simulation(db):
    """
    Test that simulates the exact issue:
    1. Create minimal session
    2. Update current_question_index to 1
    3. Fetch session again - should show current_question_index = 1
    """

    # Setup DAO
    session_dao = InterviewSessionDAO()

    # Create session with minimal data
    session_create = InterviewSessionCreate(
        candidate_id=1,  # Minimal test data
        interview_id=1,  # Minimal test data
        status=InterviewSessionStatus.ACTIVE,
        current_question_index=0
    )
    session = session_dao.create(db, obj_in=session_create)
    print(f"Created session: {session.id} with current_question_index: {session.current_question_index}")

    # FIRST ITERATION - Simulate answering first question
    print("\n=== FIRST ITERATION ===")

    # Fetch session (like in process_chat_message)
    session = session_dao.get(db=db, id=session.id)
    assert session is not None, "Session should exist"
    print(f"Fetched session: current_question_index = {session.current_question_index}")
    assert session.current_question_index == 0

    # Simulate the logic that determines we should advance to next question
    current_index = session.current_question_index
    new_index = 1  # Simulate advancing to next question

    print(f"Simulating advancement: current_index={current_index}, new_index={new_index}")

    # The exact code from the service
    if new_index != current_index:
        print("Condition met: new_index != current_index")

        # Update session (matching the service logic)
        session_update = InterviewSessionUpdate(
            current_question_index=new_index,
            questions_asked=session.questions_asked + 1
        )
        session = session_dao.update(db=db, db_obj=session, obj_in=session_update)  # type: ignore
        print(f"Updated session: current_question_index = {session.current_question_index}")

        # Verify the update worked
        assert session.current_question_index == 1, f"Expected current_question_index=1, got {session.current_question_index}"
        assert session.questions_asked == 1, f"Expected questions_asked=1, got {session.questions_asked}"

        current_index = new_index
        print(f"Set current_index = {current_index}, questions_asked = {session.questions_asked}")

    # SECOND ITERATION - This is where the bug manifests
    print("\n=== SECOND ITERATION ===")

    # Fetch session again (like in the next call to process_chat_message)
    session = session_dao.get(db=db, id=session.id)
    assert session is not None, "Session should exist"
    print(f"Fetched session again: current_question_index = {session.current_question_index}")

    # This should be 1, not 0!
    assert session.current_question_index == 1, f"BUG: Expected current_question_index=1, but got {session.current_question_index}"
    assert session.questions_asked == 1, f"BUG: Expected questions_asked=1, but got {session.questions_asked}"

    print("✅ SUCCESS: Session progression works correctly!")


def test_multiple_session_updates(db):
    """Test multiple consecutive updates to ensure persistence."""

    session_dao = InterviewSessionDAO()

    # Create minimal session
    session_create = InterviewSessionCreate(
        candidate_id=1,
        interview_id=1,
        status=InterviewSessionStatus.ACTIVE,
        current_question_index=0
    )
    session = session_dao.create(db, obj_in=session_create)

    # Test multiple updates
    for i in range(1, 5):
        print(f"\n--- Update {i} ---")

        # Fetch fresh from DB
        session = session_dao.get(db=db, id=session.id)
        assert session is not None, "Session should exist"
        print(f"Before update: current_question_index = {session.current_question_index}")

        # Update (simulating the service logic)
        session_update = InterviewSessionUpdate(
            current_question_index=i,
            questions_asked=session.questions_asked + 1
        )
        session = session_dao.update(db=db, db_obj=session, obj_in=session_update)  # type: ignore
        print(f"After update: current_question_index = {session.current_question_index}, questions_asked = {session.questions_asked}")

        # Verify immediately
        assert session.current_question_index == i
        assert session.questions_asked == i, f"Expected questions_asked={i}, got {session.questions_asked}"

        # Verify by fetching fresh from DB
        fresh_session = session_dao.get(db=db, id=session.id)
        assert fresh_session is not None, "Fresh session should exist"
        print(f"Fresh fetch: current_question_index = {fresh_session.current_question_index}, questions_asked = {fresh_session.questions_asked}")
        assert fresh_session.current_question_index == i, f"Expected current_question_index={i}, got {fresh_session.current_question_index}"
        assert fresh_session.questions_asked == i, f"Expected questions_asked={i}, got {fresh_session.questions_asked}"

    print("✅ SUCCESS: Multiple updates work correctly!")
