from fastapi import FastAPI, Depends, HTTPException, status, File
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Lecture, Attendance
from schemas import UserCreate, UserAction, LectureStatusResponse
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
@app.post("/login")
async def login_user(user: UserAction, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status_code": status.HTTP_200_OK, "message": "Login successful"}


# 3. Lecture Status Check Endpoint
@app.get("/lecture/status/{lecture_id}", response_model=LectureStatusResponse)
async def lecture_status(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    lecture_started = lecture.start_time is not None and (lecture.end_time is None or lecture.end_time > datetime.now())
    return LectureStatusResponse(lecture_started=lecture_started)


# 4. Student Check-in Endpoint
@app.post("/lecture/checkin")
async def checkin_student(lecture_id: int, user: UserAction, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.username == user.username, User.is_teacher == False).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

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
async def start_lecture(lecture_id: int, user: UserAction, db: Session = Depends(get_db)):
    # Check if the user is a teacher
    teacher = db.query(User).filter(User.username == user.username, User.is_teacher == True).first()
    if not teacher:
        raise HTTPException(status_code=403, detail="User is not a teacher")

    # Check if the lecture exists and is associated with this teacher
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id, Lecture.teacher_id == teacher.id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    # Start the lecture by setting the start time
    if lecture.start_time is not None:
        raise HTTPException(status_code=400, detail="Lecture already started")
    lecture.start_time = datetime.now()
    db.commit()
    return {"status_code": status.HTTP_200_OK, "message": "Lecture started"}


# 6. End Lecture Endpoint
@app.post("/lecture/end")
async def end_lecture(lecture_id: int, user: UserAction, db: Session = Depends(get_db)):
    # Check if the user is a teacher
    teacher = db.query(User).filter(User.username == user.username, User.is_teacher == True).first()
    if not teacher:
        raise HTTPException(status_code=403, detail="User is not a teacher")

    # Check if the lecture exists and is associated with this teacher
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id, Lecture.teacher_id == teacher.id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    # End the lecture by setting the end time
    if lecture.end_time is not None:
        raise HTTPException(status_code=400, detail="Lecture already ended")
    lecture.end_time = datetime.now()
    db.commit()
    return {"status_code": status.HTTP_200_OK, "message": "Lecture ended"}


@app.get("/report")
async def generate_report(user: UserAction, db: Session = Depends(get_db)):
    # Authenticate the user (ensure it's an admin or authorized user)
    # ...
    # Check if the user is a teacher
    teacher = db.query(User).filter(User.username == user.username, User.is_teacher == True).first()
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
    return File(file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
