from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Role(str, Enum):
    TEACHER='teacher'
    STUDENT='student'


class UserBase(BaseModel):
    email: str
    nickname: str
    role: Role


class UserPost(UserBase):
    password: str

class UserORM(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True
class UserForToken(UserBase):
    user_id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


