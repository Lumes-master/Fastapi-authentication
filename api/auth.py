import json
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from schemas.codes import Codes
from schemas.messages import Message
from schemas.profiles import ProfileDB
from schemas.users import Token, UserPost, UserORM
from services.auth_service import UserService, get_current_user
from services.email_service import EmailService
from services.profile_service import ProfileService
from services.reset_pass_service import ResetPassService

auth_router = APIRouter(prefix='/auth')


@auth_router.post('/registration')
async def register_new_user(
        data: UserPost,
        background_task: BackgroundTasks,
        service: UserService = Depends()
)->Token:
    user = service.create_user(data)
    background_task.add_task(
        service.create_profile,
        username=user.username,
        user_id=user.user_id
    )
    return service.create_token(user)

@auth_router.post('/sign-in')
async def auth_user(data: OAuth2PasswordRequestForm = Depends(), service:UserService = Depends())->Token:
    return service.authenticate_user(data.username, data.password)

@auth_router.post('/forget-password', response_model=Message)
async def send_reset_code(
        email: str,
        background_task: BackgroundTasks,
        service: UserService = Depends(),
        email_service: EmailService = Depends()
):
    new_code = service.save_new_code(email)
    background_task.add_task(
        email_service.send_reset_code,
        email,
        new_code
    )
    message = Message(message = f"Check your email {email},"
                          f" to get further instructions")
    return message


@auth_router.post('/change-password-code')
async def change_pass_via_code(
        code: str,
        new_pas1: str,
        new_pas2: str,
        service: UserService=Depends())->UserORM:
    user = service.change_password_with_code(
        code, pas1=new_pas1, pas2=new_pas2
    )
    return user

@auth_router.post('/create-code', response_model=Codes)
def create_restore_code(data: Codes, session: ResetPassService = Depends())->Codes:
    new_code = session.create_code(data)
    return new_code

