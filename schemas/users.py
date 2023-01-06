from datetime import datetime
from typing import Optional
from pydantic import BaseModel


from schemas.profiles import ProfileBase

class CodeBase(BaseModel):

    id: int
    reset_code: Optional[str] = None
    verify_code: Optional[str] = None
    expires_reset_code: Optional[datetime]= None
    user_id: int
    'user: UserORM'

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    username: str

class UserPost(UserBase):
    password: str

class UserORM(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime
    code: Optional[CodeBase]
    profile: Optional[ProfileBase]

    class Config:
        orm_mode = True

class UserForToken(UserBase):
    user_id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'




