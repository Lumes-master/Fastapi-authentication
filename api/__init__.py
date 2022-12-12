from fastapi import APIRouter

from api.auth import auth_router
from api.profiles import prof_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(prof_router)