from fastapi import APIRouter, Depends

from schemas.users import Token, UserPost, UserORM
from services.users_service import UserService, get_current_user

users_router = APIRouter(
    prefix='/users'
)

@users_router.get("/{id}", response_model=UserORM)
async def get_user_by_id(
        id: int,
        service: UserService = Depends(),
        user:UserORM = Depends(get_current_user)):
    return service.get_user_by_id(user.user_id)

# @users_router.get('/')
# async def get_users(service:UserService=Depends()) ->list[UserPost]:
#     return service.get_users()

@users_router.post('/registration')
async def register_new_user(data: UserPost, service: UserService = Depends())->Token:
    return service.create_user(data)

@users_router.post('/sign-in/')
async def auth_user(email: str, password: str,
                    service: UserService = Depends())->Token:
    return service.authenticate_user(email, password)
