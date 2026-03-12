from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import uv, age_groups, melanoma


# Create the FastAPI application instance.
app = FastAPI(
    title="Sun Safety Backend",
    description="Backend API for UV index, melanoma incidence, and myth-buster data.",
    version="1.0.0",
)

# Define the frontend origins allowed to call this backend.
# These are common local development URLs for a Vue/Vite frontend.

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://*.vercel.app",  # This allows any Vercel preview/deployment URL
]

# CORS middleware so the browser allows the frontend to make requests to this backend from a different origin.
# allow_credentials=True is useful if cookies/auth are added later. allow_methods=["*"] allows all HTTP methods for now. allow_headers=["*"] allows standard frontend request headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary root endpoint. This is only for confirming that the backend starts correctly.
@app.get("/")
def root():
    return {
        "message": "Sun Safety backend is running."
    }

# Register the UV router with the FastAPI app.
app.include_router(uv.router)

# Resgiter the Age Group Router with the FastAPI app.
app.include_router(age_groups.router)

# Register the Melanoma Incidence Router with the FastAPI app.
app.include_router(melanoma.router)
