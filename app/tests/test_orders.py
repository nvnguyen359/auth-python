# Test CRUD + filter order 
# app/tests/test_orders.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_orders_empty():
    response = client.get("/orders")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert isinstance(body["data"], list)
