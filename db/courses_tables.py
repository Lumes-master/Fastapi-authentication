
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from sqlalchemy_utils import URLType
from db.user_tables import User
from db.database import Base
from db.mixins import TimeStamp


class Course(TimeStamp, Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    created_by = relationship(User)
    section = relationship('Section', back_populates='course')
    student_courses = relationship('StudentCourses', back_populates='course')


class Section(Base):
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'))

    course = relationship('Course', back_populates='section')
    content_blocks = relationship('ContentBlock', back_populates='section')


class ContentBlock(Base):
    __tablename__ = 'content_blocks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    type = Column(URLType, nullable=True)
    content = Column(Text, nullable=True)
    section_id = Column(Integer, ForeignKey('sections.id'))

    section = relationship('Section', back_populates='comtent_blocks')
    completed_content_blocks = relationship(
        'CompletedContentBlock',
        back_populates='comtent_blocks'
    )

