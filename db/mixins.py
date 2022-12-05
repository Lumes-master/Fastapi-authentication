from datetime import datetime
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import Column, DateTime

@declarative_mixin
class TimeStamp:
    """creating extra date fields in children classes automaticly"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable = False)
    updated_at = Column(DateTime, default = datetime.utcnow, nullable = False)