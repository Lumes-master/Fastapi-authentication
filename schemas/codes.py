from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Codes(BaseModel):

    id: int
    reset_code: Optional[str] = None
    user_id: int
    expires_at: Optional[datetime]= None
    class Config:
        orm_mode = True