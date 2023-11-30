from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base  # Base is the declarative base from SQLAlchemy


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    is_teacher = Column(Boolean, default=False)

    lectures = relationship("Lecture", back_populates="teacher")
    attendances = relationship("Attendance", back_populates="student")


class Lecture(Base):
    __tablename__ = 'lectures'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)

    teacher = relationship("User", back_populates="lectures")
    attendances = relationship("Attendance", back_populates="lecture")


class Attendance(Base):
    __tablename__ = 'attendances'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    lecture_id = Column(Integer, ForeignKey('lectures.id'))
    checkin_time = Column(DateTime)

    student = relationship("User", back_populates="attendances")
    lecture = relationship("Lecture", back_populates="attendances")
