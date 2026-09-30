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


def generate_workout_gemini(
    goal: str,
    intensity: str,
    age: int,
    weight: float,
) -> str:

    prompt = f"""
You are FitBuddy AI, a friendly fitness assistant.

Create a personalized beginner-friendly workout plan.

User details:
Age: {age}
Weight: {weight} kg
Fitness Goal: {goal}
Workout Intensity: {intensity}

Include:

1. Warm-up
2. Main workout
3. Sets and repetitions
4. Rest time
5. Cool-down
6. Short safety reminder

Make the plan practical, clear and easy to follow.

Do not diagnose medical conditions.
Do not recommend dangerous exercises.
Keep the response concise.
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
                    f"Trying Gemini model: {model} "
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

                # Retry only temporary server/rate-limit errors
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
                        f"{model} failed after 3 attempts. "
                        "Trying next model..."
                    )
                    break

                # Do not retry authentication or other permanent errors
                raise

    raise RuntimeError(
        "Gemini is temporarily unavailable. "
        f"Last error: {last_error}"
    )