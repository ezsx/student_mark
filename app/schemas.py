from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    full_name: str
    is_teacher: bool = False


class UserAction(BaseModel):
    username: str


class LectureAction(BaseModel):
    title: str
    username: str
