
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from starlette import status

from schemas.users import CodeBase
from db.models import User as DB_User, Code
from services.auth_service import UserService
from services.mixins_code import MixinCode


class ResetPassService(MixinCode):

    @staticmethod
    def check_code_expires(code: Code) -> bool:
        now = datetime.utcnow()
        return code.expires_reset_code > now

    @classmethod
    def check_password_equal(cls, pas1: str, pas2: str) -> bool:
        return pas1 == pas2

    def __init__(self, user_service: UserService = Depends()):
        self.service = user_service

    async def get_code_by_reset_code(self, reset_code:str)->Code:
        query = select(Code).where(Code.reset_code == reset_code). \
            options(selectinload(Code.user))
        result = await self.service.session.execute(query)
        code = result.scalar()
        print(code, code.reset_code)
        return code

    async def create_code(self, data: CodeBase)->Code:
        print('we are in create code func')
        code_data = data.dict()
        code_bd = Code(**code_data)
        self.service.session.add(code_bd)
        await self.service.session.commit()
        print('created code')
        return code_bd


    async def insert_reset_code(self, user: DB_User)->str:
        user.code.reset_code = self.generate_code()
        user.code.expires_reset_code = datetime.utcnow() + timedelta(minutes=15)
        await self.service.session.commit()
        return user.code.reset_code


    async def save_new_reset_code(self, email: str)->str:
        user = await self.service.get_user_by_email(email)

        print(user.code)
        if user.code:
            return await self.insert_reset_code(user)
        else:
            db_code = Code(
                reset_code = self.generate_code(),
                user_id = user.user_id,
                expires_reset_code = datetime.utcnow() + timedelta(minutes=15)
            )
            self.service.session.add(db_code)
            await self.service.session.commit()
            return db_code.reset_code


    async def change_password_with_code(
            self, reset_code: str, pas1: str, pas2: str
    )->DB_User:

        if not self.check_password_equal(pas1, pas2):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="passwords don't match ")
        code = await self.get_code_by_reset_code(reset_code)
        if code is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Code, you have passed, doesn't match. Please, "
                       "copy from email and paste it again, or ask for reset "
                       "code once more")
        if not self.check_code_expires(code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Code time expired, please ask for reset "
                       "code once more"
            )

        code.user.hashed_password = self.hash_password(pas1)
        code.reset_code = None
        code.expires_reset_code = None
        code.user.updated_at = datetime.utcnow()
        await self.service.session.merge(code.user)
        await self.service.session.commit()
        return code.user


