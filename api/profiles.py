from fastapi import APIRouter, Depends

from schemas.profiles import ProfileDB
from schemas.users import UserORM, UserForToken
from services.auth_service import get_current_user, UserService
from services.profile_service import ProfileService

prof_router = APIRouter(prefix="/profiles")

@prof_router.get('/')
async def get_profiles(service: ProfileService=Depends()) ->list[ProfileDB]:
    return service.get_all_profiles()

@prof_router.get("/user", response_model=UserForToken)
async def get_user_by_id(
        service: UserService = Depends(),
        user:UserForToken= Depends(get_current_user)):
    return user