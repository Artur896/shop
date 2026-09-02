from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.ai.routes import router as ai_router
from app.api.routes.activity import router as activity_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.integrations import router as integrations_router
from app.api.routes.invitations import router as invitations_router
from app.api.routes.items import router as items_router
from app.api.routes.lists import router as lists_router
from app.api.routes.members import router as members_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.push import router as push_router
from app.api.routes.ws import router as ws_router
from app.core.config import settings
from app.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(lists_router)
app.include_router(items_router)
app.include_router(members_router)
app.include_router(invitations_router)
app.include_router(notifications_router)
app.include_router(push_router)
app.include_router(integrations_router)
app.include_router(activity_router)
app.include_router(ai_router)
app.include_router(ws_router)
