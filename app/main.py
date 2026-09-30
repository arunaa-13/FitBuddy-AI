from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routes import router


settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()

    yield


app = FastAPI(

    title=settings.app_name,

    description=(
        "AI-powered 7-day fitness plan "
        "generator using Gemini models."
    ),

    version="1.0.0",

    lifespan=lifespan,
)


app.mount(

    "/static",

    StaticFiles(
        directory=BASE_DIR / "static"
    ),

    name="static",
)


app.include_router(router)


@app.get("/health")
def health():

    settings = get_settings()

    return {

        "status": "ok",

        "app": settings.app_name,

        "ai_mode": (
            "demo"
            if (
                settings.demo_mode
                or not settings.gemini_api_key
            )
            else "gemini"
        ),

        "workout_model": (
            settings.gemini_workout_model
        ),

        "fast_model": (
            settings.gemini_fast_model
        ),
    }