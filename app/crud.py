from sqlalchemy.orm import Session

from .models import User, WorkoutPlan


# ============================================================
# USER FUNCTIONS
# ============================================================

def save_user(
    db: Session,
    username: str,
    user_id: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
):
    """
    Create a new user or update an existing user.
    """

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user is None:
        user = User(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        db.add(user)

    else:
        user.username = username
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity

    db.commit()
    db.refresh(user)

    return user


def get_user_by_user_id(
    db: Session,
    user_id: str,
):
    """
    Find a user using the user's custom ID.
    """

    return (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )


def get_all_users(
    db: Session,
):
    """
    Return all users.
    """

    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )


# ============================================================
# WORKOUT PLAN FUNCTIONS
# ============================================================

def save_plan(
    db: Session,
    user_id: int,
    workout_plan: str,
    nutrition_tip: str,
):
    """
    Save a newly generated workout plan.
    """

    plan = WorkoutPlan(
        user_id=user_id,
        workout_plan=workout_plan,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


def get_plan_by_user_id(
    db: Session,
    user_id: str,
):
    """
    Get the most recent workout plan for a user.

    The route receives the user's custom string ID,
    while WorkoutPlan.user_id stores the internal
    database integer ID.
    """

    user = get_user_by_user_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        return None

    return (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id)
        .order_by(WorkoutPlan.created_at.desc())
        .first()
    )


def get_all_plans(
    db: Session,
):
    """
    Return all workout plans.
    """

    return (
        db.query(WorkoutPlan)
        .order_by(WorkoutPlan.created_at.desc())
        .all()
    )


def update_plan(
    db: Session,
    user_id: str,
    updated_plan: str,
):
    """
    Update the most recent workout plan belonging
    to the specified user.
    """

    plan = get_plan_by_user_id(
        db=db,
        user_id=user_id,
    )

    if plan is None:
        return None

    plan.workout_plan = updated_plan
    plan.updated_at = __import__("datetime").datetime.utcnow()

    db.commit()
    db.refresh(plan)

    return plan