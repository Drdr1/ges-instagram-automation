from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, engine, Base
from app.routes import onboarding, admin, settings, dm  
from app.config import get_settings

settings_config = get_settings()

app = FastAPI(
    title="GES Instagram Automation API",
    description="Instagram automation with smooth onboarding and DM capabilities",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Java integration - adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(onboarding.router)
app.include_router(admin.router)
app.include_router(settings.router)
app.include_router(dm.router)  

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "GES Instagram Automation API",
        "version": "1.0.0",
        "endpoints": {
            "onboarding": "/api/onboarding/*",
            "admin": "/api/admin/*",
            "dm": "/api/dm/*",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
