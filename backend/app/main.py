# backend/app/main.py (Updated for Schedulers)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

### --- NAYA BADLAV (START) --- ###
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
import pytz
### --- NAYA BADLAV (END) --- ###

from .config import settings
from .database import engine, Base
from .routes import user_routes, medication_routes, appointment_routes, contact_routes, tip_routes

### --- NAYA BADLAV (REMINDERS KE LIYE) --- ###
from .reminders import send_daily_reminders


# Database Initialization
Base.metadata.create_all(bind=engine)

### --- NAYA BADLAV (LIFESPAN MANAGER) --- ###
# Yeh code app ke start hote hi scheduler ko chalu karega aur band hote hi band karega.
scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Kolkata"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App start hone par
    print("Starting scheduler...")
    # Har din subah 7 baje chalne ke liye schedule karein.
    scheduler.add_job(send_daily_reminders, trigger=CronTrigger(hour=7, minute=0))
    scheduler.start()
    print("Scheduler started. Daily reminders scheduled for 7:00 AM IST.")
    yield
    # App band hone par
    print("Shutting down scheduler...")
    scheduler.shutdown()
    print("Scheduler shut down.")

# FastAPI Application Instance
app = FastAPI(
    title="Senior Health Support API",
    description="API for managing senior citizen's health information.",
    version="1.0.0",
    lifespan=lifespan  # Lifespan manager ko yahan jodein
)
### --- NAYA BADLAV (END) --- ###


# Serve Static Files (Profile Pictures)
app.mount("/profile_pics", StaticFiles(directory="static/profile_pics"), name="profile_pics")

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:8501",
]
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(user_routes.router)
app.include_router(medication_routes.router)
app.include_router(appointment_routes.router)
app.include_router(contact_routes.router)
app.include_router(tip_routes.router)

# Root Endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Senior Health Support API! Visit /docs for API documentation."}
