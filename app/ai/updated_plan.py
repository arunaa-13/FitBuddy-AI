import os
import time

from dotenv import load_dotenv
from google import genai


# Load .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file."
    )

client = genai.Client(api_key=API_KEY)


def update_workout_plan(
    original_plan: str,
    feedback: str,
) -> str:

    prompt = f"""
You are FitBuddy AI.

A user has an existing workout plan and has provided feedback.
Modify the workout plan based on the feedback.

ORIGINAL WORKOUT PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Create an improved workout plan.

Keep:
- The user's original goal where possible
- The plan practical and beginner-friendly
- Appropriate rest periods
- A warm-up and cool-down
- A short safety reminder

Do not diagnose medical conditions.
Do not recommend dangerous exercises.

Return only the updated workout plan.
"""

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
    ]

    last_error = None

    for model in models:

        for attempt in range(3):

            try:
                print(
                    f"Updating workout with {model} "
                    f"(attempt {attempt + 1}/3)"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                if response.text:
                    return response.text.strip()

            except Exception as exc:

                last_error = exc
                error_text = str(exc)

                if "503" in error_text or "429" in error_text:

                    if attempt < 2:
                        wait_time = 2 ** attempt

                        print(
                            f"Gemini temporarily unavailable. "
                            f"Retrying in {wait_time} seconds..."
                        )

                        time.sleep(wait_time)
                        continue

                    print(
                        f"{model} failed. "
                        "Trying the next model..."
                    )
                    break

                raise

    raise RuntimeError(
        "Gemini could not update the workout plan. "
        f"Last error: {last_error}"
    )