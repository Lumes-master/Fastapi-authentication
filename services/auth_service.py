from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from starlette import status

from db.database import get_db, Session
from db.models import User as DB_User, Profile as DB_Profile, Code
from schemas.messages import Message
from schemas.users import UserPost, UserORM, UserForToken
from services.mixins_code import MixinCode
from services.reset_pass_service import ResetPassService
from settings import settings
from schemas.users import Token


oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/sign-in/")

def get_current_user(token: str = Depends(oauth2))->UserForToken:
    return UserService.validate_token(token)

class UserService(MixinCode):

    @classmethod
    def hash_password(cls, raw_password)->str:
        return bcrypt.hash(raw_password)

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

    def __init__(self, db:Session = Depends(get_db)):
        self.session = db

    def create_profile(self, username:str, user_id: int):
        """Automatically activated while confirm registration"""
        profile = DB_Profile(username=username, user_id=user_id)
        self.session.add(profile)



    def create_user(self, data: UserPost)->DB_User:
        pas_service = ResetPassService()
        user = DB_User(
            email=data.email,
            hashed_password=pas_service.hash_password(data.password),
            role = data.role,
            username = data.username
        )
        self.session.add(user)
        self.session.commit()
        return user


    def confirm_registration(self, email, code)->Message:
        user = self._get_user_by_email(email)
        now = datetime.utcnow()
        if now > user.created_at + timedelta(days=1):
            self.session.delete(user)
            self.session.commit()
            message = Message(message="Time for confirmation has expired. Please,"
                              "pass registration procedure anew.")

            return message

        if user.code != code:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Wrong credentials'
            )
        user.activated=True
        self.create_profile(username=user.username, user_id=user.user_id)
        self.session.commit()
        message = Message(message="Your registration is completed")
        return message

    def create_verifying_code(self, user_id):
        code = Code(
            user_id=user_id,
            verify_code=self.generate_code(),
                            )
        self.session.add(code)
        self.session.commit()
        return code

    def authenticate_user(self, username: str, password: str)->Token:
        user = self._get_user_by_username(username=username)
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail= "Email or password is not correct"
            )
        return self.create_token(user)

    ### CRUD

    def get_users(self)->list[UserORM]:
        users = self.session.query(DB_User).all()
        return users


    def _get_user_by_id(self, user_id:int)->DB_User:
        user = self.session.query(DB_User).filter_by(user_id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User doesn't exists"
            )
        return user

    def get_user_by_id(self, user_id: int):
        return self._get_user_by_id(user_id=user_id)


    def _get_user_by_username(self, username:str):
        user = self.session.query(DB_User).filter_by(username=username).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User doesn't exists")
        return user

    def _get_user_by_email(self, email: str):
        user = self.session.query(DB_User).filter_by(email=email).first()
        if not user:
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="User with such email doesn't exists"
                )
        return user

    def delete_user_by_email(self, email: str = None):
        user = self._get_user_by_email(email)
        self.session.delete(user)
        self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


    def update_user(self, email: str, data: UserPost)->DB_User:
        user = self._get_user_by_email(email)
        for i in data.dict():
            user.i = data.get(i)
        self.session.save(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_all_profiles(self)->list[DB_Profile]:
        profile_list = self.session.query(DB_Profile).all()
        return profile_list

    def test_user_profile_create(self, user_id: int)->DB_User:
        user = self._get_user_by_id(user_id)
        user.username = 'test'
        self.create_profile(username=user.username, user_id=user.user_id)
        self.session.commit()
        return user

    def test_user_profile_delete(self, user_id: int)->Message:
        user = self._get_user_by_id(user_id)
        profile =  user.profile
        self.session.delete(profile)
        self.session.delete(user)
        self.session.commit()
        return Message('profiles were deleted')





