from typing import Optional

from pydantic import BaseModel


class ProfileBase(BaseModel):

    nick_name: str
    user_id: int
    is_active:bool = True


class ProfilePost(ProfileBase):
    pass

class ProfileDB(ProfileBase):
    id: int