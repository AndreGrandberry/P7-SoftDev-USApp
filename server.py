from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.exceptions import Unauthorized

from provider import get_clubs, get_competitions

app = Flask(__name__)
# You should change the secret key in production!
app.secret_key = "something_special"


@app.route("/")
def index():
    """Homepage"""
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    """Use the session object to store the club information across requests"""

    clubs = get_clubs()
    if "email" not in request.form or not request.form["email"]:
        return render_template("index.html", error="Email is required."), 400

    email = request.form["email"]
    club_list = [item for item in clubs if item["email"] == email]
    if not club_list:
        return render_template("index.html", error="Email not found. Please try again."), 401

    club = club_list[0]
    session["club"] = club

    return redirect(url_for("summary"))


@app.route("/summary")
def summary():
    """Custom "homepage" for logged in users"""
    if "club" not in session:
        return "Unauthorized", 401

    club = session["club"]
    competitions = get_competitions()

    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>")
def book(competition):
    """Book spots in a competition page"""
    club = session["club"]

    competitions = get_competitions()
    matching_comps = [comp for comp in competitions if comp["name"] == competition]

    found_competition = matching_comps[0]

    if found_competition:
        return render_template("booking.html", club=club, competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return redirect(url_for("summary"))


@app.route("/book", methods=["POST"])
def book_spots():
    """This page is only accessible through a POST request (form validation)"""
    club = session["club"]
    competitions = get_competitions()

    matching_comps = [
        comp for comp in competitions if comp["name"] == request.form["competition"]
    ]

    competition = matching_comps[0]

    spots_required = int(request.form["spots"])
    club_points = int(club["points"])

    if spots_required > club_points:
        return render_template("welcome.html", club=club, competitions=competitions, error="Not enough points."), 403

    if spots_required <= 0:
        return render_template("welcome.html", club=club, competitions=competitions,
                               error="Invalid number of spots."), 400

    competition["spotsAvailable"] = int(competition["spotsAvailable"]) - spots_required
    flash("Great-booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/logout")
def logout():
    """We delete session data in order to log the user out"""
    del session["club"]
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
