from datetime import datetime, timedelta
from fastapi import BackgroundTasks, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from starlette import status

from db.database import get_db, Session
from db.models import User, Profile as DB_Profile
from schemas.users import UserPost, UserORM, UserForToken
from settings import settings

from schemas.users import Token


oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/sign-in/")

def get_current_user(token: str = Depends(oauth2))->UserORM:
    return UserService.validate_token(token)

class UserService:

    @classmethod
    def hash_password(cls, raw_password)->str:
        return bcrypt.hash(raw_password)

    @classmethod
    def verify_password(cls, raw_password, hash_passewrd)->bool:
        return bcrypt.verify(raw_password, hash_passewrd)

    @classmethod
    def create_token(cls, user:User)->Token:
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
    def validate_token(cls, token: str)->UserORM:
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
            user = UserORM.parse_obj(user_data)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )
        return user

    def __init__(self, db:Session = Depends(get_db)):
        self.session = db

    def authenticate_user(self, email: str, password: str)->Token:
        user = self._get_user_by_email(email=email)
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail= "Email or password is not correct"
            )
        return self.create_token(user)

    ### CRUD

    def create_profile(self, username:str, user_id: int):
        profile = DB_Profile(username=username, user_id=user_id)
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)



    def create_user(self,
                    data: UserPost,
                    back: BackgroundTasks)->Token:
        user = User(
            email=data.email,
            hashed_password=self.hash_password(data.password),
            role = data.role,
            nickname = data.nickname

        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        self.create_profile(username=user.username, user_id=user.user_id)
        return self.create_token(user)


    def get_users(self)->list[UserORM]:
        users = self.session.query(User).all()
        return users

    def _get_user_by_id(self, id:int=None)->User:
        user = self.session.query(User) \
            .filter_by(User.user_id == id).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail='User doesn''t exists'
            )

        return user

    def _get_user_by_email(self, email:str):
        user = self.session.query(User) \
            .filter_by(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail='User doesn''t exists')
        return user

    def get_user_by_id(self, id:int):
        return self._get_user_by_id(id)
    def delete_user_by_email(self, email: str = None):
        user = self._get_user_by_email(email)
        self.session.delete(user)
        self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    def update_user(self, email: str, data: UserPost)->User:
        user = self._get_user_by_email(email)
        for i in data.dict():
            user.i = data.get(i)
        self.session.save(user)
        self.session.commit()
        self.session.refresh(user)
        return user





