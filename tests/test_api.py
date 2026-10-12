"""Basic tests for the sentiment API."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_positive():
    response = client.post("/predict", json={"text": "I love this"})
    assert response.status_code == 200
    assert response.json()["sentiment"] == "positive"

def test_predict_negative():
    response = client.post("/predict", json={"text": "this is terrible"})
    assert response.status_code == 200
    assert response.json()["sentiment"] == "negative"
