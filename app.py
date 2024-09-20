import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import datetime

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    return render_template("index.html")


@app.route("/create_group", methods=["GET", "POST"])
@login_required
def create_group():
    if request.method == "POST":
        rows = db.execute("SELECT * FROM groups WHERE groupname = ?", request.form.get("groupname"))
        if not request.form.get('groupname'):
            return apology("Must Provide Group Name", 400)
        elif len(rows) != 0:
            return apology("Group name already in use", 400)
        else:
            db.execute("INSERT INTO groups (groupname, admin_id) VALUES (?, ?)", request.form.get("groupname"), session["user_id"] )
            group_id = db.execute("SELECT id FROM groups WHERE groupname = ?", request.form.get("groupname"))
            db.execute("INSERT INTO members (group_id, user_id) VALUES (?, ?)", group_id[0]['id'], session["user_id"] )
            return redirect("/add_member")
    else:
        return render_template("create_group.html")


@app.route("/add_member", methods=["GET", "POST"])
@login_required
def add_member():
    groups = db.execute("SELECT groupname FROM groups WHERE admin_id = ?", session["user_id"])  # a list of all the groups user is admin of


    if request.method == "POST":

        switch = False
        for group in groups:
            if request.form.get("groupname") == group['groupname']:
                switch = True  # admittedly confusing, basically just making sure that submitted group is admined by user
        if not switch:
            return apology("You are not admin of this group/ No group selected", 403)

        group_id = db.execute("SELECT id FROM groups WHERE groupname = ?", request.form.get('groupname'))[0]['id'] # id of selected group
        group_members = db.execute("SELECT user_id FROM members WHERE group_id = ?", group_id)

        if not request.form.get("membername"):
            return apology("Must fill out 'Member Name' field", 403)

        new_member_id = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("membername"))
        if len(new_member_id) != 1:
            return apology("No users found with provided username", 403)

        for member in group_members:
            if member['user_id'] == new_member_id[0]['id']:
                return apology("User already in this group", 403)

        else:
            db.execute("INSERT INTO members (group_id, user_id) VALUES (?,?)", group_id, new_member_id[0]['id'])
            return render_template("add_member.html", groups = groups, confirmation = "GROUP MEMBER ADDED SUCCESSFULLY")
    else:
        return render_template("add_member.html", groups = groups)

@app.route("/my_groups")
@login_required
def my_groups():
    groups = db.execute("SELECT groupname, id FROM groups WHERE id IN (SELECT group_id FROM members WHERE user_id = ?)", session["user_id"])
    groups_dict = {}
    for group in groups:
        group_list = []
        members = db.execute("SELECT username FROM users WHERE id IN (SELECT user_id FROM members WHERE group_id = ?)", group['id'])
        for member in members:
            group_list.append(member)
        groups_dict[group['groupname']] = group_list


    return render_template("my_groups.html", groups = groups_dict)

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        movies = db.execute("SELECT title, year FROM movies WHERE title = ?", request.form.get('movie'))
        return render_template("search.html", movies=movies)
    else:
        return render_template("search.html")

@app.route("/add_watchlist", methods=["GET", "POST"])
@login_required
def add_watchlist():
    groups = db.execute("SELECT groupname FROM groups WHERE id IN (SELECT group_id FROM members WHERE user_id = ?)", session["user_id"])
    if request.method == "POST":
        if not request.form.get('groupname'):
            return apology("Must select group")
        group_id = db.execute("SELECT id FROM groups WHERE groupname = ?", request.form.get('groupname'))[0]['id']
        movie_id = db.execute("SELECT id FROM movies WHERE title = ? AND year = ?", request.form.get('movie'), request.form.get('year'))
        if len(movie_id) != 1:
            return apology("Movie not found in database")
        submissions = db.execute ("SELECT * FROM watch_list WHERE group_id = ? AND movie_id = ? AND user_id = ?", group_id, movie_id[0]['id'], session["user_id"])
        if len(submissions) != 0:
            return apology("You have already submitted this movie to this watchgroup")
        db.execute("INSERT INTO watch_list (group_id, movie_id, user_id) VALUES (?, ?, ?)", group_id, movie_id[0]['id'], session["user_id"])
        confirmation = '"' +request.form.get('movie') + '"' + " Sucessfully Added"
        return render_template("add_watchlist.html", groups=groups, confirmation=confirmation)
    else:
        return render_template("add_watchlist.html", groups=groups)


@app.route("/rankings")
@login_required
def rankings():
    
    groups = db.execute("SELECT groupname, id FROM groups WHERE id IN (SELECT group_id FROM members WHERE user_id = ?)", session["user_id"])
    for group in groups:
        movies = db.execute("SELECT movies.title, movies.year, COUNT(watch_list.movie_id) as frequency \
                            FROM movies INNER JOIN watch_list ON movies.id=watch_list.movie_id \
                            WHERE watch_list.group_id = ? GROUP BY watch_list.group_id, watch_list.movie_id \
                            ORDER BY COUNT(watch_list.movie_id) DESC;", group['id'])
        group['movies'] = movies

    return render_template("rankings.html", groups = groups)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if not request.form.get("username") or len(rows) != 0:
            return apology("must provide unique username", 400)
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)
        else:
            hash = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash )
            return redirect('/')

    else:
        return render_template("register.html")


