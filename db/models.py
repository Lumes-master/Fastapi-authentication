from datetime import datetime

import sqlalchemy as sq
from sqlalchemy.orm import relationship, declarative_mixin
from sqlalchemy import  DateTime
from db.database import Base


@declarative_mixin
class TimeStamp:
    """creating extra date fields in children classes automaticly"""
    created_at = sq.Column(DateTime, default=datetime.utcnow, nullable = False)
    updated_at = sq.Column(DateTime, default = datetime.utcnow, nullable = False)
class User(TimeStamp, Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True, index=True)
    email = sq.Column(sq.String(100), unique=True, index=True, nullable=False)
    hashed_password = sq.Column(sq.Text, unique=True)
    username = sq.Column(sq.String(50), nullable=False)
    role = sq.Column(sq.Text)
    profile = relationship('Profile', back_populates='owner', uselist=False)
    code = relationship('Code', back_populates='user', uselist=False)


class Profile(Base):
    __tablename__ = 'profiles'

    profile_id = sq.Column(sq.Integer, primary_key=True, index=True)
    username = sq.Column(sq.String(50), nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    is_active = sq.Column(sq.Boolean, default=True)
    owner = relationship('User', back_populates='profile')

class Code(Base):
    __tablename__ = 'codes'

    id = sq.Column(sq.Integer, primary_key=True, index=True)
    reset_code = sq.Column(sq.String(50), nullable=True)
    expires_at = sq.Column(sq.DateTime, nullable=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))
    user = relationship('User', back_populates='code')
