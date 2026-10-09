from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.user.router import router as user_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.0.1",
    description="MedVision AI Backend",
)

# ---------------------------------------------------------------------------
# CORS / Security
# ---------------------------------------------------------------------------
# Replaces SecurityConfig.java:
#   - csrf.disable()          → not applicable (FastAPI doesn't use CSRF by default)
#   - httpBasic.disable()     → not applicable (no built-in basic auth)
#   - formLogin.disable()     → not applicable (no built-in form login)
#   - permitAll() on routes   → all routes are open by default in FastAPI;
#                                add Depends() guards when you need auth
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(user_router)


# ---------------------------------------------------------------------------
# Health endpoint – replaces HealthController.java
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["health"])
def health():
    """GET /api/health – same response as the Spring HealthController."""
    return {"message": "MedVision AI backend is running"}
