from enum import Enum
from users import UserBase

class ContentType(Enum, str):
    lesson = "LESSON"
    QUIZ = 'quiz'
    ASSIGNMENT = 'assignment'



