from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Codes(BaseModel):

    id: int
    reset_code: Optional[str] = None
    verify_code: Optional[str] = None
    expires_reset_code: Optional[datetime]= None
    user_id: int

    class Config:
        orm_mode = True