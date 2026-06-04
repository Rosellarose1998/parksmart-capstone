from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.database import Base, SessionLocal, get_db, init_db
from app.models.user import User, UserRole
from app.utils.auth import hash_password

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    import app.database as db_module

    monkeypatch.setattr(db_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(db_module, "engine", engine)

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def app():
    application = create_app({"TESTING": True})
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session():
    session = get_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("Admin123!"),
        full_name="Test Admin",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "Admin123!"})
    return response.get_json()["access_token"]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_register_and_login(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@test.com", "password": "Password123!", "full_name": "Test User"},
    )
    assert response.status_code == 201
    assert response.get_json()["email"] == "user@test.com"

    response = client.post("/api/v1/auth/login", json={"email": "user@test.com", "password": "Password123!"})
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_create_lot_requires_admin(client, admin_token):
    response = client.post(
        "/api/v1/parking/lots",
        json={"name": "Test Lot", "address": "123 Test St"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    assert response.get_json()["name"] == "Test Lot"


def test_create_reservation(client, admin_token):
    lot_response = client.post(
        "/api/v1/parking/lots",
        json={"name": "Test Lot", "address": "123 Test St"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    lot_id = lot_response.get_json()["id"]

    spot_response = client.post(
        "/api/v1/parking/spots",
        json={"lot_id": lot_id, "spot_number": "A-01"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    spot_id = spot_response.get_json()["id"]

    client.post(
        "/api/v1/auth/register",
        json={"email": "driver@test.com", "password": "Password123!", "full_name": "Driver"},
    )
    login = client.post("/api/v1/auth/login", json={"email": "driver@test.com", "password": "Password123!"})
    user_token = login.get_json()["access_token"]

    start = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    end = (datetime.now(UTC) + timedelta(hours=3)).isoformat()

    response = client.post(
        "/api/v1/reservations",
        json={"spot_id": spot_id, "start_time": start, "end_time": end},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 201
    assert response.get_json()["spot_id"] == spot_id
