import os
import pytest
from fastapi.testclient import TestClient

# ensure env vars loaded for DB connection
from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), ".env"))

from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_primary():
    payload = {"email": "a@x.com", "phoneNumber": "123"}
    resp = client.post("/identify", json=payload)
    assert resp.status_code == 200
    data = resp.json()["contact"]
    assert data["primaryContactId"] == 1
    assert data["emails"] == ["a@x.com"]
    assert data["phoneNumbers"] == ["123"]
    assert data["secondaryContactIds"] == []


def test_create_secondary_on_new_info():
    client.post("/identify", json={"email": "a@x.com", "phoneNumber": "123"})
    resp = client.post("/identify", json={"email": "b@x.com", "phoneNumber": "123"})
    assert resp.status_code == 200
    data = resp.json()["contact"]
    assert data["primaryContactId"] == 1
    assert set(data["emails"]) == {"a@x.com", "b@x.com"}
    assert data["phoneNumbers"] == ["123"]
    assert data["secondaryContactIds"] == [2]


def test_link_two_primaries():
    client.post("/identify", json={"email": "x@a.com", "phoneNumber": None})
    client.post("/identify", json={"email": None, "phoneNumber": "999"})
    resp = client.post("/identify", json={"email": "x@a.com", "phoneNumber": "999"})
    assert resp.status_code == 200
    data = resp.json()["contact"]
    assert data["primaryContactId"] == 1
    assert data["secondaryContactIds"] == [2]


def test_secondary_query_after_merge():
    # create two primaries then merge
    client.post("/identify", json={"email": "u@p.com", "phoneNumber": "555"})
    client.post("/identify", json={"email": None, "phoneNumber": "717171"})
    client.post("/identify", json={"email": "u@p.com", "phoneNumber": "717171"})
    # now query using the demoted phone
    resp = client.post("/identify", json={"phoneNumber": "717171"})
    assert resp.status_code == 200
    assert resp.json()["contact"]["primaryContactId"] == 1


def test_missing_both_fields():
    resp = client.post("/identify", json={})
    assert resp.status_code == 400
