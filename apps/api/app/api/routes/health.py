from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.redis import get_redis
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    checks = {"database": "down", "redis": "down"}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "up"
    except Exception:
        pass

    try:
        redis = get_redis()
        await redis.ping()
        checks["redis"] = "up"
    except Exception:
        pass

    healthy = all(v == "up" for v in checks.values())
    return {"status": "healthy" if healthy else "degraded", "checks": checks}
