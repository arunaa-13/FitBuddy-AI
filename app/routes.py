from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db


router = APIRouter()


# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


# -------------------------------------------------------------------
# HOME PAGE
# -------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Displays the FitBuddy homepage.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "FitBuddy - AI Fitness Plan Generator"
        },
    )


# -------------------------------------------------------------------
# GENERATE WORKOUT
# -------------------------------------------------------------------

@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Receives user information and generates a personalized
    workout plan and nutrition/recovery tip.

    The AI functions will be connected from the app/ai package.
    """

    # Import AI functions here rather than at module startup.
    # This keeps the application easier to debug while the project
    # is being assembled.
    try:
        from .ai.gemini_generator import generate_workout_gemini
        from .ai.gemini_flash_generator import (
            generate_nutrition_tip_with_flash,
        )

        workout_plan = generate_workout_gemini(
            goal=goal,
            intensity=intensity,
            age=age,
            weight=weight,
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            goal=goal,
            age=age,
            weight=weight,
        )

    except Exception as exc:
        # Temporary fallback so the application can still display
        # a useful result if Gemini is not configured yet.
        workout_plan = (
            "AI workout generation is currently unavailable.\n\n"
            f"Requested goal: {goal}\n"
            f"Intensity: {intensity}\n"
            f"Age: {age}\n"
            f"Weight: {weight} kg\n\n"
            f"Technical message: {exc}"
        )

        nutrition_tip = (
            "AI nutrition guidance is currently unavailable. "
            "Please configure the Gemini API key."
        )

    # Save user and plan information once the database models are
    # available.
    try:
        from .crud import save_user, save_plan

        user = save_user(
            db=db,
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        save_plan(
            db=db,
            user_id=user.id,
            workout_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        database_user_id = user.id

    except Exception:
        # Database persistence will be enabled when the CRUD/models
        # files are connected.
        database_user_id = user_id

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": username,
            "user_id": database_user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
        },
    )


# -------------------------------------------------------------------
# SUBMIT FEEDBACK
# -------------------------------------------------------------------

@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Receives user feedback and asks Gemini to revise the
    previously generated workout plan.
    """

    original_plan = ""

    # Retrieve the user's existing plan.
    try:
        from .crud import get_plan_by_user_id

        plan = get_plan_by_user_id(
            db=db,
            user_id=user_id,
        )

        if plan:
            original_plan = plan.workout_plan

    except Exception:
        pass

    # Generate the revised plan.
    try:
        from .ai.updated_plan import update_workout_plan

        updated_plan = update_workout_plan(
            original_plan=original_plan,
            feedback=feedback,
        )

    except Exception as exc:
        updated_plan = (
            "The workout plan could not be updated using Gemini.\n\n"
            f"Original plan:\n{original_plan}\n\n"
            f"Feedback:\n{feedback}\n\n"
            f"Technical message: {exc}"
        )

    # Update the database.
    try:
        from .crud import update_plan

        update_plan(
            db=db,
            user_id=user_id,
            updated_plan=updated_plan,
        )

    except Exception:
        pass

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": "",
            "user_id": user_id,
            "goal": "",
            "intensity": "",
            "workout_plan": updated_plan,
            "nutrition_tip": "",
            "feedback_submitted": True,
        },
    )


# -------------------------------------------------------------------
# ADMIN - VIEW ALL USERS
# -------------------------------------------------------------------

@router.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Displays all registered users and their workout plans.
    """

    users = []
    plans = []

    try:
        from .crud import get_all_users, get_all_plans

        users = get_all_users(db)
        plans = get_all_plans(db)

    except Exception:
        pass

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "plans": plans,
        },
    )