from flask import request
import pytest

from server import app


def test_homepage():
    """Test the homepage works (HTTP status 200 OK)"""
    with app.test_client() as c:
        resp = c.get("/")
        assert resp.status_code == 200


def test_login():
    """Tests a login action"""
    with app.test_client() as c:
        resp = c.post(
            "/login", data={"email": "john@simplylift.co"}, follow_redirects=True
        )
        # We should be redirected to the summary page
        assert request.path == "/summary"
        # The status code should be 200 OK
        assert resp.status_code == 200
        # The email of the user logged in is displayed on the page
        assert "john@simplylift.co" in resp.data.decode()


def test_login_invalid_email():
    """Tests login with an email not in the database"""
    with app.test_client() as c:
        resp = c.post("/login", data={"email": "notfound@example.com"})
        assert resp.status_code == 401
        assert b"Email not found" in resp.data


def test_login_missing_email():
    """Tests login with a missing email field"""
    with app.test_client() as c:
        resp = c.post("/login", data={})
        assert resp.status_code == 400
        assert b"Email is required" in resp.data


def test_login_empty_email():
    """Test login with empty email field"""
    with app.test_client() as c:
        resp = c.post("/login", data={"email": ""})
        assert resp.status_code == 400
        assert b"Email is required" in resp.data


def test_protected_route_without_login():
    """Test accessing a protected route without authentication"""
    with app.test_client() as c:
        resp = c.get("/summary")
        assert resp.status_code == 401
        assert b"Unauthorized" in resp.data