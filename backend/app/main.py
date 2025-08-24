# backend/app/main.py

from contextlib import asynccontextmanager

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.reminders import send_daily_reminders
from app.routes import (
    appointment_routes,
    contact_routes,
    medication_routes,
    tip_routes,
    user_routes,
)


# --- Database Initialization ---
# This command creates all the database tables defined in our models.
# It checks if the tables exist before creating them, so it's safe to run on every startup.
Base.metadata.create_all(bind=engine)


# --- Application Lifespan Management ---
# The lifespan context manager allows us to run code on application startup and shutdown.
# Here, we use it to start and stop the background task scheduler.

# Initialize the scheduler with the Indian Standard Time (IST) timezone.
scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Kolkata"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown events.
    - On startup: Schedules and starts the daily reminder job.
    - On shutdown: Shuts down the scheduler gracefully.
    """
    print("Application startup: Starting scheduler...")
    # Schedule the `send_daily_reminders` function to run every day at 7:00 AM IST.
    scheduler.add_job(send_daily_reminders, trigger=CronTrigger(hour=7, minute=0))
    scheduler.start()
    print("Scheduler started. Daily reminders are scheduled for 7:00 AM IST.")
    
    yield  # The application runs while the context manager is active.
    
    print("Application shutdown: Shutting down scheduler...")
    scheduler.shutdown()
    print("Scheduler shut down successfully.")


# --- FastAPI Application Instance ---
app = FastAPI(
    title="Senior Health Support API",
    description="API for managing a senior citizen's health information, including medications, appointments, and reminders.",
    version="1.0.0",
    lifespan=lifespan,  # Attach the lifespan manager to the app.
)


# --- Static Files ---
# Mount a directory to serve static files. This is used for serving
# user-uploaded profile pictures. The URL will be '/profile_pics/...'.
app.mount("/profile_pics", StaticFiles(directory="static/profile_pics"), name="profile_pics")


# --- CORS (Cross-Origin Resource Sharing) Configuration ---
# This middleware allows the frontend (running on a different origin)
# to communicate with this backend API.
origins = [
    "http://localhost",
    "http://localhost:8501",  # Default Streamlit port
]
# Add the frontend URL from settings if it's defined.
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# --- API Routers ---
# Include the routers from the 'routes' package. This keeps the API
# endpoints organized in separate files.
app.include_router(user_routes.router)
app.include_router(medication_routes.router)
app.include_router(appointment_routes.router)
app.include_router(contact_routes.router)
app.include_router(tip_routes.router)


# --- Root Endpoint ---
@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {
        "message": "Welcome to the Senior Health Support API! Visit /docs for the interactive API documentation."
    }
