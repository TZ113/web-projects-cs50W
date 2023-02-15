import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import requests
import urllib.parse
from functools import wraps
from validate_email import validate_email
import random
import string
import shutil


ALLOWED_EXTENSIONS = {'txt', 'rtf', 'doc', 'pdf', 'epub', 'png', 'jpeg', 'jpg', 'gif', 'bmp', 'mp3', 'wav', 'aac', 'm4a', 'flac', 'wma', 'mp4', 'avi', 'mkv', 'flv', 'zip', '.file'}
# Configure application
app = Flask(__name__)


app.config['MAIL_SERVER']='smtp.elasticemail.com'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'blue27846@gmail.com'
app.config['MAIL_PASSWORD'] = 'E5D975E4B5601D4155D460FD6C9E413C0427'
mail = Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = 'static/uploads'
app.config["MAX_CONTENT_LENGTH"] = 101 * 1024 * 1024


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///files.db")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


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
    table_data = db.execute("SELECT id, filename, size, upload_time FROM files WHERE user_id = ? ORDER BY filename", session["user_id"])
    for i in range(len(table_data)):
        table_data[i]["download"] = url_for('.download', filename = table_data[i]["filename"])
        table_data[i]["delete"] = url_for('.delete', filename = table_data[i]["filename"])
        if table_data[i]["size"] > 1024 * 1024:
            table_data[i]["size"] = f'{table_data[i]["size"] / (1024 * 1024):.2f}Mb'
        elif table_data[i]["size"] > 1024:
            table_data[i]["size"] = f'{table_data[i]["size"] / (1024): .2f}Kb'
        else:
            table_data[i]["size"] = f'{table_data[i]["size"]: .2f}Bytes'
    return render_template("index.html", table_index=table_data)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

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
    """Register user"""
    if request.method == "POST":
        session["username"] = request.form.get("username")
        session["email"] = request.form.get("email")
        if not session["username"]:
            return apology("must provide username")
        elif len(session["username"]) < 4:
            return apology("username must have at least four characters")
        elif not session["email"]:
            return apology("must provide e-mail address")
        elif not validate_email(session["email"]):
            return apology("provide valid email address")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif len(request.form.get("password")) < 8:
            return apology("password must be at least eight characters long")
        elif not request.form.get("confirmation"):
            return apology("must confirm password")
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password doesn't match")
        else:
            row = db.execute("SELECT * FROM users WHERE username = ?", session["username"])
            if len(row) != 0:
                return apology("user already exists")
            session["token"] = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k = 32))
            msg = Message(session["token"], sender = "blue27846@gmail.com", recipients = [session["email"]])
            msg.body = session["token"]
            mail.send(msg)
        session["hash"] = generate_password_hash(request.form.get("password"))
        return render_template("verify_email.html")

    else:
        return render_template("register.html")


@app.route("/verify_email", methods = ["POST"])
def verify_email():
    token_user = request.form.get("token")
    print(token_user)
    print(session["token"])
    if not token_user or token_user != session["token"]:
        session.clear()
        return apology("token doesn't match")
    try:
        session["user_id"] = db.execute("INSERT INTO users (username, e_mail, hash) VALUES (?, ?, ?)", session["username"], session["email"], session["hash"])
        os.mkdir(os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"])))
    except:
        return apology("an error occured")
    flash("Account created.. Enjoy!")
    return redirect("/")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/change_psswd_check", methods = ["GET", "POST"])
@app.route("/change_psswd", methods = ["POST"])
@login_required
def change_psswd():
    if request.method == "POST":
        if request.path == "/change_psswd":
            if not request.form.get("new_psswd"):
                return apology("provide your new password")
            elif len(request.form.get("new_psswd")) < 8:
                return apology("password must be at least eight characters long")
            db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(request.form.get("new_psswd")), session["user_id"])
            flash("Updated")
            return redirect("/")

        c_psswd_hash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        if not request.form.get("psswd"):
            return apology("provide your current password")
        elif not check_password_hash(c_psswd_hash[0]["hash"], request.form.get("psswd")):
            return apology("password doesn't match")
        return render_template("/change_psswd.html")

    else:
        return render_template("/change_psswd_check.html")


@app.route("/change_email_psswd_check", methods = ["GET", "POST"])
@app.route("/change_email", methods = ["POST"])
@login_required
def change_email():
    if request.method == "POST":
        if request.path == "/change_email":
           session["newmail"] = request.form.get("newmail")
           if validate_email(session["newmail"]):
                db.execute("UPDATE users SET e_mail = ? WHERE id = ?", session["newmail"], session["user_id"])
                flash("Updated")
                return redirect("/")
           else:
               return apology("insert a valid e-mail address")

        c_psswd_hash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        if not request.form.get("psswd"):
            return apology("provide your current password")
        elif not check_password_hash(c_psswd_hash[0]["hash"], request.form.get("psswd")):
            return apology("password doesn't match")
        return render_template("/change_email.html")

    else:
        return render_template("/change_email_psswd_check.html")


@app.route("/delete_account", methods = ["POST"])
@login_required
def delete_account():
    try:
        shutil.rmtree(os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"])))
        db.execute("DELETE FROM files WHERE user_id = ?", session["user_id"])
        db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
        session.clear()
    except:
        return apology("an error occured")
    session.clear()
    return jsonify("done")


@app.route("/upload", methods=["GET", "POST"])
@app.route("/yay")
@login_required
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if allowed_file(file.filename):
            try:
                path = os.path.join(app.config['UPLOAD_FOLDER'], str(session["user_id"]), secure_filename(file.filename))
                file.save(path)
                size = os.path.getsize(path)
                db.execute("INSERT INTO files (user_id, filename, size) VALUES (?, ?, ?)", session["user_id"], file.filename, size)
                file.close()
            except:
                return apology("error error ")
        else:
            file.close()
            return apology("I just sharpened my TEETH! Meow!!")

        return redirect(request.url)

    else:
        if request.path == "/yay":
            flash("File successfully uploaded")
            return redirect("/upload")

        return render_template("/upload.html")


@app.route("/download/<string:filename>")
@login_required
def download(filename):
        return send_from_directory(os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"])), secure_filename(filename), as_attachment=True)


@app.route("/delete/<string:filename>")
@login_required
def delete(filename):
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"]), secure_filename(filename)))
        db.execute("DELETE FROM files WHERE user_id = ? AND filename = ?", session["user_id"], filename)
        flash("file successfully deleted")
    except:
        return apology("an error occured")
    return redirect("/")


@app.route("/check_filenames", methods = ["POST"])
@login_required
def filenames():
    filename = request.form.get("filename")
    print(filename)
    filenames = db.execute("SELECT filename FROM files WHERE user_id = ?", session["user_id"])
    for i in range(len(filenames)):
        if filename == filenames[i]["filename"]:
            return jsonify("exists")
    return jsonify("nope")


@app.route("/delete_to_replace", methods = ["POST"])
@login_required
def delete_to_replace():
    filename = request.form.get("filename")
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"]), secure_filename(filename)))
        db.execute("DELETE FROM files WHERE user_id = ? AND filename = ?", session["user_id"], filename)
    except:
        return apology("an error occured")
    return jsonify("done")


@app.route("/sort", methods = ["POST"])
@app.route("/category", methods = ["POST"])
@login_required
def sort_and_category():
    category = request.form.get("category")
    sort = request.form.get("sort")
    table_data = []
    if category == '' or category == "all":
        table_data = db.execute("SELECT * FROM files WHERE user_id = ? ORDER BY filename", session["user_id"])
    elif category == "audio":
        table_data = db.execute("SELECT * FROM files WHERE user_id = ? AND (filename LIKE '%.mp3' OR filename LIKE '%.wav' OR filename LIKE '%.aac' OR filename LIKE '%.flac' OR filename LIKE '%.m4a' OR filename LIKE '%.wma') ORDER BY filename", session["user_id"])
    elif category == "video":
        table_data = db.execute("SELECT * FROM files WHERE user_id = ? AND (filename LIKE '%.mp4' OR filename LIKE '%.mkv' OR filename LIKE '%.avi' OR filename LIKE '%.flv') ORDER BY filename", session["user_id"])
    elif category == "image":
        table_data = db.execute("SELECT * FROM files WHERE user_id = ? AND (filename LIKE '%.jpg' OR filename LIKE '%.jpeg' OR filename LIKE '%.png' OR filename LIKE '%.gif') ORDER BY filename", session["user_id"])
    elif category == "docs":
        table_data = db.execute("SELECT * FROM files WHERE user_id = ? AND (filename LIKE '%.txt' OR filename LIKE '%.doc' OR filename LIKE '%.pdf' OR filename LIKE '%.epub') ORDER BY filename", session["user_id"])
    else:
        table_data = db.execute("SELECT * FROM files WHERE user_id = ? AND filename LIKE '%.zip' ORDER BY filename", session["user_id"])

    if sort == '' or sort == "namesc":
        table_data = sorted(table_data, key = lambda i: i['filename'])
    elif sort == 'namedesc':
        table_data = sorted(table_data, key = lambda i: i['filename'], reverse = True)
    elif sort == 'size':
        table_data = sorted(table_data, key = lambda i: i['size'], reverse = True)
    elif sort == 'uploaded':
        table_data = sorted(table_data, key = lambda i: i['upload_time'])
    for i in range(len(table_data)):
        table_data[i]["download"] = url_for('.download', filename = table_data[i]["filename"])
        table_data[i]["delete"] = url_for('.delete', filename = table_data[i]["filename"])
        if table_data[i]["size"] > 1024 * 1024:
            table_data[i]["size"] = f'{table_data[i]["size"] / (1024 * 1024):.2f}Mb'
        elif table_data[i]["size"] > 1024:
            table_data[i]["size"] = f'{table_data[i]["size"] / (1024): .2f}Kb'
        else:
            table_data[i]["size"] = f'{table_data[i]["size"]: .2f}Bytes'
    return jsonify(table_data)
