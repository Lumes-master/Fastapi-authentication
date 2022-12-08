import sqlalchemy as sq
from enum import Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from db.database import Base
from db.mixins import TimeStamp

class User(TimeStamp, Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True, index=True)
    email = sq.Column(sq.String(100), unique=True, index=True, nullable=False)
    hashed_password = sq.Column(sq.Text, unique=True)
    username = sq.Column(sq.String(50), nullable=False)
    role = sq.Column(sq.Text)
    profile = relationship('Profile', back_populates='owner', uselist=False)


class Profile(Base):
    __tablename__ = 'profiles'

    profile_id = sq.Column(sq.Integer, primary_key=True, index=True)
    username = sq.Column(sq.String(50), nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    is_active = sq.Column(sq.Boolean, default=True)
    owner = relationship('User', back_populates='profile')
