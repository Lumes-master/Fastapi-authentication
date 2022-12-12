import uuid
from datetime import datetime, timedelta
from fastapi import BackgroundTasks, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from starlette import status

from db.database import get_db, Session
from db.models import User as DB_User, Profile as DB_Profile, Code
from schemas.users import UserPost, UserORM, UserForToken
from settings import settings

from schemas.users import Token


oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/sign-in/")

def get_current_user(token: str = Depends(oauth2))->UserForToken:
    return UserService.validate_token(token)

class UserService:

    @classmethod
    def check_password_equal(cls, pas1: str, pas2: str) -> bool:
        return pas1 == pas2

    @classmethod
    def genarate_code(cls) -> str:
        code = str(uuid.uuid1())
        return code

    @classmethod
    def hash_password(cls, raw_password)->str:
        return bcrypt.hash(raw_password)

    @classmethod
    def verify_password(cls, raw_password, hash_passewrd)->bool:
        return bcrypt.verify(raw_password, hash_passewrd)

    @classmethod
    def create_token(cls, user: DB_User)->Token:

        user_data = UserForToken.from_orm(user)
        print('1', user_data)
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

    def authenticate_user(self, username: str, password: str)->Token:
        user = self._get_user_by_username(username=username)
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
                    )->DB_User:
        user = DB_User(
            email=data.email,
            hashed_password=self.hash_password(data.password),
            role = data.role,
            username = data.username

        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user


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

    def check_code_expires(self, code: Code)->bool:
        now = datetime.utcnow()
        return code.expires_at > now


    def save_new_code(self, email: str)->str:
        user = self.session.query(DB_User).\
            filter_by(email=email).first()
        if not user:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail= "Email is incorrect"
            )
        code= self.session.query(Code).filter_by(user_id = user.user_id).first()
        if code:
            code.reset_code = self.genarate_code()
            code.expires_at = datetime.utcnow() + timedelta(minutes = 15)
            self.session.merge(code)
            self.session.commit()
            return code.reset_code

        db_code = Code(
            reset_code = self.genarate_code(),
            user_id = user.user_id
        )
        self.session.add(db_code)
        self.session.commit()
        return db_code.reset_code


    def change_password_with_code(
            self, code: str, pas1: str, pas2: str)->DB_User:
        if not self.check_password_equal(pas1, pas2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="passwords don't match ")
        code_from_db = self.session.query(Code).\
            filter_by(reset_code=code).first()
        if not code_from_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code, you have passed, doesn't match. Please, "
                       "copy from email and paste it again, or ask for reset "
                       "code once more")
        if not self.check_code_expires(code_from_db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Code time expired, please ask for reset "
                       "code once more"
            )
        user = self.session.query(DB_User).join(Code).filter(Code.reset_code==code).first()
        user.hashed_password = self.hash_password(pas1)
        self.session.merge(user)
        self.session.commit()
        return user






