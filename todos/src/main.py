from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.repository import get_all_todos, create_todo, get_user, create_user, validate_user
from config import config

app = Flask("todos")
app.secret_key = config.get('APP', 'secret_key')



@app.route("/todos")
def list_todos():
    if "user_id" not in session:
        return redirect(url_for("login"))

    todos = get_all_todos(session["user_id"])
    return render_template("todos.html", todos=todos, username=session["username"])

@app.route("/todos/new", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form["title"]
    description = request.form["description"]
    create_todo(title, description, user_id=session["user_id"])
    flash("Todo added!", "success")
    return redirect(url_for("list_todos"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login = request.form["username"]
        password = request.form["password"]

        if get_user(login):
            flash("User already exists!", "error")
            return redirect(url_for("register"))

        create_user(login, password)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["username"]
        password = request.form["password"]

        user = validate_user(login, password)
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("list_todos"))
        else:
            flash("Invalid credentials", "error")
        

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


app.run(host="0.0.0.0", port=3000, debug=True)
