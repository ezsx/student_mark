from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    full_name: str
    is_teacher: bool = False


class UserResponse(BaseModel):
    username: str
    full_name: str
    is_teacher: bool


class UserAction(BaseModel):
    username: str


class LectureAction(BaseModel):
    username: str
    title: str
    lat: float  # Latitude
    lng: float  # Longitude


