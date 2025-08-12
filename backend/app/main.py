# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # For allowing frontend communication

# Import database and models
from .database import engine, Base 

# Import all your routers
from .routes import user_routes
from .routes import medication_routes
from .routes import appointment_routes
from .routes import contact_routes
from .routes import tip_routes
# Import other routes as you create them (e.g., contact_routes, tip_routes)


# --- Database Initialization ---
# This line creates all the tables defined in your models (User, Medication, Appointment, etc.)
# in your PostgreSQL database when the application starts.
Base.metadata.create_all(bind=engine)


# --- FastAPI Application Instance ---
# Here, the FastAPI application object 'app' is created.
app = FastAPI(
    title="Senior Health Support API",
    description="API for managing senior citizen's health information like medications, appointments, and contacts.",
    version="1.0.0",
)


# --- CORS (Cross-Origin Resource Sharing) Configuration ---
# This middleware is crucial to allow your Streamlit frontend (which runs on a different port/origin)
# to communicate with your FastAPI backend.
origins = [
    "http://localhost",        # For local testing
    "http://localhost:8501",   # Default port for Streamlit
    # You might need to add your Streamlit Cloud URL here if you deploy it
    # "https://your-streamlit-app-url.streamlit.app", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Specifies which origins are allowed to make requests
    allow_credentials=True,        # Allow cookies, authorization headers, etc.
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Allow all headers
)


# --- Include Routers ---
# These lines attach your specific API endpoints (defined in user_routes, medication_routes, etc.)
# to the main FastAPI application instance 'app'.
app.include_router(user_routes.router)
app.include_router(medication_routes.router)
app.include_router(appointment_routes.router)
app.include_router(contact_routes.router)
app.include_router(tip_routes.router)
# Uncomment or add these as you create their respective files and content:
# app.include_router(contact_routes.router)
# app.include_router(tip_routes.router)


# --- Root Endpoint (Optional) ---
# This is a simple endpoint to check if the API is running.
@app.get("/")
def root():
    return {"message": "Welcome to the Senior Health Support API! Visit /docs for API documentation."}