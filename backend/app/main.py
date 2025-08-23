# backend/app/main.py (Updated for Deployment)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import settings to make CORS dynamic
from .config import settings

# Import database and models
from .database import engine, Base 

# Import all your routers
from .routes import user_routes, medication_routes, appointment_routes, contact_routes, tip_routes

# --- Database Initialization ---
# This line creates all the tables defined in your models when the application starts.
Base.metadata.create_all(bind=engine)

# --- FastAPI Application Instance ---
app = FastAPI(
    title="Senior Health Support API",
    description="API for managing senior citizen's health information like medications, appointments, and contacts.",
    version="1.0.0",
)

# --- Serve Static Files (Profile Pictures) ---
# This is a CRITICAL step. It tells FastAPI that any request to a path starting
# with "/profile_pics" should be served as a file from the "static/profile_pics" directory.
# Without this, you can upload photos, but you can't view them.
app.mount("/profile_pics", StaticFiles(directory="static/profile_pics"), name="profile_pics")

# --- CORS (Cross-Origin Resource Sharing) Configuration ---
# This middleware is crucial to allow your frontend to communicate with your backend.
origins = [
    "http://localhost",        # For local testing
    "http://localhost:8501",   # Default port for Streamlit
]

# Dynamically add the deployed frontend URL from your environment settings
# This makes your CORS configuration work in both development and production.
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Specifies which origins are allowed to make requests
    allow_credentials=True,        # Allow cookies, authorization headers, etc.
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Allow all headers
)

# --- Include Routers ---
# These lines attach your specific API endpoints to the main FastAPI application.
app.include_router(user_routes.router)
app.include_router(medication_routes.router)
app.include_router(appointment_routes.router)
app.include_router(contact_routes.router)
app.include_router(tip_routes.router)

# --- Root Endpoint (Optional) ---
# This is a simple endpoint to check if the API is running.
@app.get("/")
def root():
    return {"message": "Welcome to the Senior Health Support API! Visit /docs for API documentation."}
