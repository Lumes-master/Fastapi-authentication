from fastapi import Depends

from db.database import get_db, Session
from schemas.users import UserPost


class ProfileService:

    @classmethod
    def create_profile(cls, user:UserPost):
        profile = ProfileService()
    def __init__(self, session:Session=Depends(get_db())):
        self.session = session