from fastapi import APIRouter

from api.users_api import users_router

users_router
router = APIRouter()
router.include_router(users_router)