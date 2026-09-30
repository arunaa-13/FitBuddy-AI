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


def generate_nutrition_tip_with_flash(
    goal: str,
    age: int,
    weight: float,
) -> str:

    prompt = f"""
You are FitBuddy AI, a friendly fitness and nutrition assistant.

Create a short nutrition and recovery guide.

User details:
Age: {age}
Weight: {weight} kg
Fitness Goal: {goal}

Include:

1. Simple nutrition recommendation
2. General protein guidance
3. Hydration advice
4. One recovery/lifestyle tip

Keep it practical and beginner-friendly.

Do not diagnose medical conditions.
Do not prescribe medication.
Keep the answer concise.
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

                # Retry temporary errors
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

                # Don't retry permanent errors
                raise

    raise RuntimeError(
        "Gemini is temporarily unavailable. "
        f"Last error: {last_error}"
    )