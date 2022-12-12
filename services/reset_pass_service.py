import uuid

from fastapi import Depends, HTTPException
from starlette import status

from schemas.codes import Codes
from schemas.users import UserORM
from db.models import User as DB_User, Code, User
from db.database import Session
from db.database import get_db

class ResetPassService:

    def __init__(self, session: Session = Depends(get_db)):
        self.session = session


    def create_code(self, data: Codes)->Code:
        code_data = data.dict()
        code_bd = Code(**code_data)
        self.session.add(code_bd)
        self.session.commit()
        return code_bd



