from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy.orm import selectinload
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.database import async_get_db
from db.models import User as DB_User, Profile as DB_Profile, Code, Profile
from schemas.users import UserPost, UserORM, UserForToken, Token
from services.mixins_code import MixinCode
from settings import settings



oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/sign-in/")

def get_current_user(token: str = Depends(oauth2))->UserForToken:
    return UserService.validate_token(token)


class UserService(MixinCode):

    @classmethod
    def verify_password(cls, raw_password, hash_password)->bool:
        return bcrypt.verify(raw_password, hash_password)


    @classmethod
    def create_token(cls, user: DB_User)->Token:
        user_data = UserForToken.from_orm(user)
        time_now = datetime.utcnow()
        payload = {
            'exp': time_now + timedelta(minutes=15),
            'sub': str(user_data.user_id),
            'user': user_data.dict()
        }
        token = jwt.encode(
                payload,
                settings.jwt_secret,
                algorithm=settings.jwt_algorithm
            )
        return Token(access_token=token)


    @classmethod
    def validate_token(cls, token: str)->UserForToken:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_data = payload.get('user')
        try:
            user = UserForToken.parse_obj(user_data)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="couldn't exctract user"
            )
        return user

    @staticmethod
    def compare_verify_code(user: DB_User, code: str):
        if user.code.verify_code != code:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Wrong code'
            )

    @staticmethod
    def check_user_exists(user: DB_User):
        print('inside check', user)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email is not found"
            )

    @staticmethod
    def check_user_activated(user: DB_User):
        if user.activated is True:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="You have already activated account"
            )


    def __init__(self, db: AsyncSession = Depends(async_get_db)):
        self.session = db

    async def check_user_activation_expired(self, user:DB_User):
        now = datetime.utcnow()
        if now > user.created_at + timedelta(days=1):
            if user.code is not None:
                await self.session.delete(user.code)
                await self.session.delete(user)
                await self.session.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Time for confirmation has expired. Please,"
                           "pass registration procedure anew."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='No code to verify'
                )

    async def create_profile(self, username:str, user_id: int):
        """Automatically activated while confirm registration"""
        profile = DB_Profile(username=username, user_id=user_id)
        self.session.add(profile)
        await self.session.commit()
        print('profile was created', profile)


    async def create_user(self, data: UserPost)->DB_User:
        user = DB_User(
            email=data.email,
            hashed_password=self.hash_password(data.password),
            username = data.username
        )
        self.session.add(user)
        await self.session.commit()
        return user


    async def confirm_registration(self, email: str, code: str)->DB_User:
        user = await self._get_user_by_email(email)
        self.check_user_activated(user)
        await self.check_user_activation_expired(user)
        self.compare_verify_code(user, code)
        user.activated=True
        await self.session.commit()
        return user


    async def create_verifying_code(self, user_id):
        code = Code(
            user_id=user_id,
            verify_code=self.generate_code(),
                            )
        self.session.add(code)
        await self.session.commit()
        return code.verify_code


    async def authenticate_user(self, username: str, password: str)->Token:
        user = await self._get_user_by_username(username=username)
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail= "Email or password is not correct"
            )
        return self.create_token(user)



    async def _get_user_by_id(self, user_id:int)->DB_User:
        query = select(DB_User).where(DB_User.user_id==user_id)
        user = await self.session.execute(query)
        self.check_user_exists(user)
        return user.scalar_one_or_none()


    async def get_user_by_id(self, user_id: int):
        return await self._get_user_by_id(user_id==user_id)


    async def _get_user_by_username(self, username:str)->DB_User:
        query = select(DB_User).where(DB_User.username==username)
        user = await self.session.execute(query)
        self.check_user_exists(user)
        return user.scalar_one_or_none()


    async def _get_user_by_email(self, email: str):
        query = select(DB_User).where(DB_User.email == email).\
            options(selectinload(DB_User.code), selectinload(DB_User.profile))
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        self.check_user_exists(user)
        print('inside _get_user', user)
        return user


    async def get_user_by_email(self, email: str):
        return await self._get_user_by_email(email=email)


    async def delete_user_by_email(self, email: str = None):
        user = self._get_user_by_email(email)
        await self.session.delete(user)
        await self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


    async def update_user(self, email: str, data: UserPost)->DB_User:
        user = await self._get_user_by_email(email)
        for field, value in data:
            setattr(user, field, value)
        await self.session.commit()
        return user


    async def get_users(self)->list[UserORM]:
        query =  select(DB_User).all()
        result =  await self.session.execute(query)
        return result.scalars()




