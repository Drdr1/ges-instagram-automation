from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, engine
from app.database import Base
from app.routes import onboarding, admin, settings
from app.config import get_settings

settings_config = get_settings()

# Create FastAPI app
app = FastAPI(
    title="GES Instagram Automation",
    description="Smooth onboarding for nightlife Instagram automation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings_config.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(onboarding.router)
app.include_router(admin.router)
app.include_router(settings.router)

# Health check
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "GES Instagram Automation API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
