from fastapi import APIRouter, Depends

from schemas.users import UserForToken, UserORM
from services.auth_service import UserService

user_router = APIRouter()

@user_router.get('/user/{email}', response_model=UserORM)
async def get_user_by_email(email: str, service: UserService = Depends())->UserORM:
    user = await service.get_user_by_email(email)
    return user

