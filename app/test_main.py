from faker import Faker
from fastapi.testclient import TestClient
from main import app

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import SQLALCHEMY_DATABASE_URL  # Import your actual database URL
from models import Base  # Import your SQLAlchemy models

# Assuming your database URL is set up correctly in your_database_config
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# @pytest.fixture(autouse=True)
# def clear_database():
#     # Drop all tables and recreate them
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     yield


client = TestClient(app)

fake = Faker()

r_username = fake.user_name()
r_full_name = fake.name()
r_title = fake.sentence()

r_username_teacher = fake.user_name()
r_full_name_teacher = fake.name()

print(r_username, r_full_name, r_title, r_username_teacher, r_full_name_teacher)

def test_register_student():
    response = client.post("/register", json={
        "username": r_username,
        "full_name": r_full_name,
        "is_teacher": False
    })
    assert response.status_code == 200


def test_register_teacher():
    response = client.post("/register", json={
        "username": r_username_teacher,
        "full_name": r_full_name_teacher,
        "is_teacher": True
    })
    assert response.status_code == 200


def test_login_student():
    response = client.post("/login", json={"username": r_username})
    assert response.status_code == 200


def test_login_teacher():
    response = client.post("/login", json={"username": r_username_teacher})
    assert response.status_code == 200


def test_start_lecture():
    response = client.post("/lecture/start", json={
        "title": r_title,
        "username": r_username_teacher
    })
    print(response.content)
    assert response.status_code == 200


def test_checkin_student():
    response = client.post("/lecture/checkin", json={
        "title": r_title,
        "username": r_username
    })
    print(response.content)
    assert response.status_code == 200


def test_end_lecture():
    response = client.post("/lecture/end", json={
        "title": r_title,
        "username": r_username_teacher
    })
    print(response.content)
    assert response.status_code == 200


def test_lecture_status():
    response = client.get("/lecture/status", params={"title": r_title})
    assert response.status_code == 200


def test_generate_report():
    response = client.get("/report", params={"user": r_username_teacher})
    assert response.status_code == 200

    content_disposition = response.headers.get("content-disposition")
    content_type = response.headers.get("content-type")

    # Verify that the content disposition indicates a file attachment
    assert content_disposition is not None
    assert "attachment" in content_disposition

    # Verify the content type for an Excel file
    assert content_type in ["application/octet-stream",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

    # Optionally, check if the content length is reasonable for an Excel file (not empty or too small)
    content_length = response.headers.get("content-length")
    assert content_length is not None and int(content_length) > 0
