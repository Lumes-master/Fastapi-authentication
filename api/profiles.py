from fastapi import APIRouter, Depends

from schemas.profiles import ProfileDB
from schemas.users import  UserForToken
from services.auth_service import get_current_user, UserService


prof_router = APIRouter(prefix="/profiles")



@prof_router.get("/user", response_model=UserForToken)
async def create_profile_to_user( user_id: int,
        service: UserService = Depends()
       ):
    return service.test_user_profile_create(user_id)

@prof_router.post("/user-delete")
async def create_profile_to_user( user_id: int,
        service: UserService = Depends()
       ):
    return service.test_user_profile_delete(user_id)