from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    full_name: str
    is_teacher: bool = False


class LectureStatusResponse(BaseModel):
    lecture_started: bool


class UserAction(BaseModel):
    username: str


class ReportResponse(BaseModel):
    # This can be more complex based on your report's structure
    report: dict
