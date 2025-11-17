from flask import request

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


def test_book_more_than_12_spots():
    """Booking more than 12 spots should fail with 403 Forbidden"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "13"})
        assert resp.status_code == 403
        assert "Cannot book more than 12 places." in resp.data.decode()


def test_book_exactly_12_spots():
    """Booking exactly 12 spots should succeed (HTTP 200 OK)"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "12"})
        assert resp.status_code == 200
        assert "Cannot book more than 12 places." not in resp.data.decode()
