import uuid
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from passlib.hash import bcrypt
from starlette import status

from schemas.codes import Codes
from db.models import User as DB_User, Code
from db.database import Session
from db.database import get_db
from services.mixins_code import MixinCode


class ResetPassService(MixinCode):

    @staticmethod
    def check_code_expires(code: Code) -> bool:
        now = datetime.utcnow()
        return code.expires_at > now

    @classmethod
    def check_password_equal(cls, pas1: str, pas2: str) -> bool:
        return pas1 == pas2

    @classmethod
    def hash_password(cls, raw_password) -> str:
        return bcrypt.hash(raw_password)

    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def create_code(self, data: Codes)->Code:
        code_data = data.dict()
        code_bd = Code(**code_data)
        self.session.add(code_bd)
        self.session.commit()
        return code_bd

    def save_new_reset_code(self, email: str)->str:
        user = self.session.query(DB_User).\
            filter_by(email=email).first()
        if not user:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND,
                detail= "Email is incorrect"
            )
        code= self.session.query(Code).\
            filter_by(user_id = user.user_id).first()
        if code:
            code.reset_code = self.generate_code()
            code.expires_reset_code = datetime.utcnow() + timedelta(minutes = 15)
            self.session.merge(code)
            self.session.commit()
            return code.reset_code

        db_code = Code(
            reset_code = self.generate_code(),
            user_id = user.user_id,
            expires_reset_code = datetime.utcnow() + timedelta(minutes=15)
        )
        self.session.add(db_code)
        self.session.commit()
        return db_code.reset_code


    def change_password_with_code(
            self, code: str, pas1: str, pas2: str)->DB_User:
        if not self.check_password_equal(pas1, pas2):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="passwords don't match ")
        code_from_db = self.session.query(Code).\
            filter_by(reset_code=code).first()
        if code_from_db is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Code, you have passed, doesn't match. Please, "
                       "copy from email and paste it again, or ask for reset "
                       "code once more")
        if not self.check_code_expires(code_from_db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Code time expired, please ask for reset "
                       "code once more"
            )
        user = self.session.query(DB_User).\
            join(Code).filter(Code.reset_code==code).first()
        user.hashed_password = self.hash_password(pas1)
        user.code.reset_code = None
        self.session.merge(user)
        self.session.commit()
        return user


