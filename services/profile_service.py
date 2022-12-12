from fastapi import Depends
from db.database import get_db, Session
from db.models import Profile as DB_Profile
from schemas.users import UserPost
from schemas.profiles import ProfileDB


class ProfileService:

    def __init__(self, session:Session=Depends(get_db)):
        self.session = session

    def get_all_profiles(self)->list[DB_Profile]:
        profile_list = self.session.query(DB_Profile).all()
        return profile_list