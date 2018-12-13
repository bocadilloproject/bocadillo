"""Tests for the API snippet.

Run with the `test.sh` script.
"""
from time import sleep

import requests
import pytest


@pytest.fixture
def payload():
    return {"name": "Python Programming", "teacher": "Guido van Rossum"}


def url(path: str) -> str:
    return "http://localhost:8000" + path


def test_index():
    r = requests.get(url("/"))
    assert r.status_code == 200
    assert r.headers["content-type"] == "text/html"
    html = r.text.lower()
    assert "courses" in html
    assert "no courses yet" in html


def test_list_courses():
    r = requests.get(url("/courses/"))
    assert r.status_code == 200
    assert r.json() == []


def test_invalid_payload(payload: dict):
    payload.pop("name")
    r = requests.post(url("/courses/"), json=payload)
    assert r.status_code == 400


def test_create_course(payload: dict):
    r = requests.post(url("/courses/"), json=payload)
    assert r.status_code == 201
    assert r.json() == {"id": 1, **payload}
    print(r.json())


def test_get_course(payload: dict):
    r = requests.get(url("/courses/1"))
    assert r.status_code == 200
    course = r.json()
    assert course == {"id": 1, **payload}
    r = requests.get(url("/courses/"))
    assert course in r.json()


def test_get_non_existing_course():
    r = requests.get(url("/courses/2"))
    assert r.status_code == 404
    assert r.json() == {"error": "Not Found", "status": 404, "message": "Duh!"}


@pytest.mark.parametrize(
    "token, status", [(None, 401), ("foo", 401), ("knowntoken", 200)]
)
def test_analytics(token, status, payload: dict):
    # Analytics make take some time to update (background task)
    sleep(0.1)
    if token is not None:
        headers = {"Authorization": "Token: " + token}
    else:
        headers = {}
    r = requests.get(url("/courses/top"), headers=headers)
    assert r.status_code == status
    if status == 200:
        assert r.json() == [{"id": 1, **payload}]
