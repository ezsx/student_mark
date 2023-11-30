from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_students():
    students_data = [
        {"username": "student1", "full_name": "Student One", "is_teacher": False},
        {"username": "student2", "full_name": "Student Two", "is_teacher": False},
        # Add more students as needed
    ]
    for student in students_data:
        response = client.post("/register", json=student)
        assert response.status_code == 200
        assert response.json()["username"] == student["username"]


def test_create_teachers():
    teachers_data = [
        {"username": "teacher1", "full_name": "Teacher One", "is_teacher": True},
        {"username": "teacher2", "full_name": "Teacher Two", "is_teacher": True},
        # Add more teachers as needed
    ]
    for teacher in teachers_data:
        response = client.post("/register", json=teacher)
        assert response.status_code == 200
        assert response.json()["username"] == teacher["username"]


def test_login_student():
    login_data = {"username": "student1"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"


def test_start_lecture():
    lecture_data = {"title": "Sample Lecture", "teacher_id": 1}  # Update as needed
    response = client.post("/lecture/start", json=lecture_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Lecture started"


def test_checkin_student():
    checkin_data = {"lecture_id": 1, "username": "student1"}
    response = client.post("/lecture/checkin", json=checkin_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Check-in successful"


def test_end_lecture():
    lecture_data = {"lecture_id": 1}  # Update as needed
    response = client.post("/lecture/end", json=lecture_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Lecture ended"


def test_lecture_status():
    response = client.get("/lecture/status/1")
    assert response.status_code == 200
    assert response.json()["lecture_started"] == False


def test_generate_report():
    response = client.get("/report")
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
