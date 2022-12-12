from typing import Optional

from pydantic import BaseModel


class ProfileBase(BaseModel):

    username: str
    user_id: int
    is_active:bool = True


class ProfilePost(ProfileBase):
    pass

class ProfileDB(ProfileBase):
    id: int