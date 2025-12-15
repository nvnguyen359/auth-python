# Test login, JWT 
# app/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_invalid():
    response = client.post("/auth/login", json={"username": "nouser", "password": "wrong"})
    assert response.status_code == 401

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["mes"] == "AD-OCV1 is running"
