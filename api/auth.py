import json
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from schemas.codes import Codes
from schemas.messages import Message
from schemas.users import Token, UserPost, UserORM
from services.auth_service import UserService
from services.email_service import EmailService
from services.reset_pass_service import ResetPassService

auth_router = APIRouter(prefix='/auth')


@auth_router.post('/registration')
async def register_new_user(
        data: UserPost,
        background_task: BackgroundTasks,
        user_service: UserService = Depends(),
        email_service: EmailService = Depends()
        )->Token:
    user = user_service.create_user(data)
    background_task.add_task(
        user_service.create_profile,
        username=user.username,
        user_id=user.user_id
    )
    verify_code = user_service.create_verifying_code(user.user_id)
    background_task.add_task(
        email_service.send_hello_email(data.username, data.email, verify_code)
    )
    return user_service.create_token(user)


@auth_router.post('/confirm-registration')
def confirm_registration(email: str, code: str,
                         service: UserService=Depends())->Message:
    return service.confirm_registration(email=email, code=code)


@auth_router.post('/sign-in')
async def authenticate_user(data: OAuth2PasswordRequestForm = Depends(),
                            service:UserService = Depends())->Token:
    return service.authenticate_user(data.username, data.password)


@auth_router.post('/forget-password', response_model=Message)
async def send_reset_code(
        email: str,
        background_task: BackgroundTasks,
        service: ResetPassService = Depends(),
        email_service: EmailService = Depends()
):
    new_reset_code = service.save_new_reset_code(email)
    background_task.add_task(
        email_service.send_reset_code,
        email,
        new_reset_code
    )
    message = Message(message = f"Check your email {email},"
                          f" to get further instructions")
    return message


@auth_router.post('/reset-password-code')
async def change_pass_via_code(
        code: str,
        new_pas1: str,
        new_pas2: str,
        service: ResetPassService=Depends())->UserORM:
    user = service.change_password_with_code(
        code, pas1=new_pas1, pas2=new_pas2
    )
    return user

@auth_router.post('/create-code', response_model=Codes)
def create_restore_code(data: Codes, session: ResetPassService = Depends())->Codes:
    new_code = session.create_code(data)
    return new_code

