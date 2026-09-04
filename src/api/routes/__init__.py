from fastapi import APIRouter
from .webhook import router as webhook_router
from .health import router as health_router
from .metrics import router as metrics_router
from .admin import router as admin_router

router = APIRouter()
router.include_router(webhook_router)
router.include_router(health_router)
router.include_router(metrics_router)
router.include_router(admin_router)
