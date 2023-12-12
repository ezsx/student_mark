import math
from fastapi import FastAPI, Depends, HTTPException, status, File
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Lecture, Attendance
from schemas import UserCreate, UserAction, UserResponse, LectureAction
from fastapi.responses import FileResponse
from datetime import datetime
import pandas as pd

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1. Registration Endpoint
@app.post("/register", response_model=UserCreate)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(username=user.username, full_name=user.full_name, is_teacher=user.is_teacher)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 2. Login Endpoint
@app.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login_user(user: UserAction, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = UserResponse(
        username=db_user.username,
        full_name=db_user.full_name,
        is_teacher=db_user.is_teacher
    )
    return user_data


# 3. Lecture Status Check Endpoint
@app.get("/lecture/status")
async def lecture_status(title: str, db: Session = Depends(get_db)):
    lecture = db.query(Lecture).filter(Lecture.title == title).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    lecture_started = lecture.start_time is not None and (lecture.end_time is None or lecture.end_time > datetime.now())
    return {"status_code": status.HTTP_200_OK, "message": "Lecture started"}


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in meters
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# 4. Student Check-in Endpoint
@app.post("/lecture/checkin")
async def checkin_student(request: LectureAction, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.username == request.username, User.is_teacher == False).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    lecture = db.query(Lecture).filter(Lecture.title == request.title).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    teacher_lat = lecture.latitude
    teacher_lng = lecture.longitude

    distance = calculate_distance(request.lat, request.lng, teacher_lat, teacher_lng)

    # Check if the student is within 300 meters of the teacher
    if distance > 300:
        raise HTTPException(status_code=400, detail="Student is not within the required proximity to the teacher")

    # Check if the lecture is currently ongoing
    if lecture.start_time is None or (lecture.end_time is not None and lecture.end_time < datetime.now()):
        raise HTTPException(status_code=400, detail="Lecture is not active")

    # Register attendance
    attendance = Attendance(student_id=student.id, lecture_id=lecture.id, checkin_time=datetime.now())
    db.add(attendance)
    db.commit()
    return {"status_code": status.HTTP_200_OK, "message": "Check-in successful"}


# 5. Start Lecture Endpoint
@app.post("/lecture/start")
async def start_lecture(request: LectureAction, db: Session = Depends(get_db)):
    # Check if the user is a teacher
    teacher = db.query(User).filter(User.username == request.username, User.is_teacher == True).first()
    if not teacher:
        raise HTTPException(status_code=403, detail="User is not a teacher")

    # Check if the lecture already exists
    lecture = db.query(Lecture).filter(Lecture.title == request.title).first()

    # If the lecture does not exist, create it
    if not lecture:
        lecture = Lecture(title=request.title, teacher_id=teacher.id)
        db.add(lecture)

    # If the lecture has already started, throw an error
    elif lecture.start_time is not None:
        raise HTTPException(status_code=400, detail="Lecture already started")

    # Start the lecture and set location
    lecture.start_time = datetime.now()
    lecture.latitude = request.lat  # Set latitude
    lecture.longitude = request.lng  # Set longitude
    db.commit()
    return {"status_code": status.HTTP_200_OK, "message": "Lecture started"}


# 6. End Lecture Endpoint
@app.post("/lecture/end")
async def end_lecture(request: LectureAction, db: Session = Depends(get_db)):
    # Check if the user is a teacher
    teacher = db.query(User).filter(User.username == request.username, User.is_teacher == True).first()
    if not teacher:
        raise HTTPException(status_code=403, detail="User is not a teacher")

    # Check if the lecture exists and is associated with this teacher
    lecture = db.query(Lecture).filter(Lecture.title == request.title).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    # End the lecture by setting the end time
    if lecture.end_time is not None:
        raise HTTPException(status_code=400, detail="Lecture already ended")
    lecture.end_time = datetime.now()
    db.commit()
    return {"status_code": status.HTTP_200_OK, "message": "Lecture ended"}


@app.get("/report")
async def generate_report(user: str, db: Session = Depends(get_db)):
    # Authenticate the user (ensure it's an admin or authorized user)
    # ...
    # Check if the user is a teacher
    teacher = db.query(User).filter(User.username == user, User.is_teacher == True).first()
    if not teacher:
        raise HTTPException(status_code=403, detail="User is not a teacher")

    # Fetch lectures and attendance from the database
    lectures = db.query(Lecture).all()
    report_data = []

    for lecture in lectures:
        attendances = db.query(Attendance).filter(Attendance.lecture_id == lecture.id).all()
        for attendance in attendances:
            student = db.query(User).filter(User.id == attendance.student_id).first()
            report_data.append({
                "Lecture ID": lecture.id,
                "Lecture Title": lecture.title,
                "Student Username": student.username,
                "Check-in Time": attendance.checkin_time
            })

    # Create a pandas DataFrame
    df = pd.DataFrame(report_data)

    # Save DataFrame to an Excel file
    file_path = "attendance_report.xlsx"
    df.to_excel(file_path, index=False)

    # Return the Excel file
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename="attendance_report.xlsx")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
