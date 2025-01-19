from xmlrpc.client import Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String,DateTime,BINARY,Float,ForeignKey,Boolean
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.sql import text

SQLALCHEMY_DATABASE_URL = "sqlite:///db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


def get_cur_id(db,model):
    if db.query(model).order_by(text("id desc")).first():
        return db.query(model).order_by(text("id desc")).first().id + 1
    else:
        return 1
##############################################################################################
class StatusEnum(Enum):
    QUIZ = 'викторина'
    START = 'начальный экран'
    GUARDIANSHIP  = 'Программа опеки'
    FEEDBACK = 'Отзыв'
    ENTERQ = 'enter question'
    ENTERA = 'enter answer'
    ENTERAP = 'enter ans points'
    ENTERR = 'enter ans points'
    ENTERRPMX = 'enter res points max'
    ENTERRPMN = 'enter res points min'
    ADMINISTRATION = 'adm'


class Base(DeclarativeBase): pass

class Questions(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title        = Column(String)


class User_Condition(Base):
    __tablename__ = "user_Condition"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    TgUserId = Column(Integer, index=True)
    curent_question = Column(Integer, ForeignKey(Questions.id), index=True)
    curent_answer = Column(Integer, ForeignKey(Questions.id), index=True)
    CurentCond = Column(PgEnum(StatusEnum,
                                 name='status_enum',
                                 create_type=False),
                                 nullable=False,
                                 default=StatusEnum.START)

class Commands(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title        = Column(String)

class Answers(Base):
    __tablename__ = "answers"
    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_question    = Column(Integer, ForeignKey(Questions.id), index=True)
    title          = Column(String)
    points         = Column(Integer, index=True)

class Results(Base):
    __tablename__ = "results"
    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title          = Column(String)
    result         = Column(String)
    pointsmax      = Column(Integer, index=True)
    pointsmin      = Column(Integer, index=True)

class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stoped          = Column(Boolean)
    started         = Column(Boolean)
    curent_points   = Column(Integer, index=True)
    TgUserId        = Column(Integer, index=True)

class userAnswers(Base):
    __tablename__ = "user_answers"
    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_question    = Column(Integer, ForeignKey(Questions.id), index=True)
    id_answer      = Column(Integer, ForeignKey(Answers.id), index=True)
    id_quiz        = Column(Integer, ForeignKey(Quiz.id), index=True)
    TgUserId       = Column(Integer, index=True)


SessionLocal = sessionmaker(autoflush=False, bind=engine)
