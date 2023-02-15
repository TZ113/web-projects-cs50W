import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    table_data = db.execute("SELECT DISTINCT(symbol) FROM transactions WHERE id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?) ORDER BY symbol", session["user_id"])
    total = cash[0]['cash']
    for i in range(len(table_data)):
        api_data = lookup(table_data[i]['symbol'])
        table_data[i]['name'] = api_data['name']
        table_data[i]['price'] = api_data['price']
        shares_bought = db.execute("SELECT SUM(shares) FROM transactions WHERE transaction_type = 'buy' AND symbol = ? AND id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?)", api_data['symbol'], session["user_id"])
        shares_sold = db.execute("SELECT SUM(shares) FROM transactions WHERE transaction_type = 'sell' AND symbol = ? AND id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?)", api_data['symbol'], session['user_id'])
        print(shares_sold)
        if shares_sold[0]['SUM(shares)'] == None:
            table_data[i]["shares"] = shares_bought[0]['SUM(shares)']
        else:
            table_data[i]["shares"] = shares_bought[0]['SUM(shares)'] - shares_sold[0]['SUM(shares)']
        table_data[i]['total'] = table_data[i]['shares'] * table_data[i]['price']
        total += table_data[i]['total']

    return render_template("/index.html", table_data=table_data, cash=cash[0]['cash'], total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        api_data = lookup(request.form.get("symbol"))
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        if api_data == None:
            return apology("provide a valid symbol")
        elif not request.form.get("shares").isdigit():
            return apology("provide a valid number")
        elif api_data['price'] * int(request.form.get("shares")) > cash[0]['cash']:
            return apology("can't afford")

        transaction_id = db.execute("INSERT INTO transactions (symbol, company, shares, price, transaction_type) VALUES(?, ?, ?, ?, ?) ", api_data['symbol'], api_data['name'], int(request.form.get("shares")), api_data['price'], 'buy')
        db.execute("INSERT INTO users_transactions (user_id, transaction_id) VALUES (?, ?)", session["user_id"], transaction_id)
        cash_updated = cash[0]['cash'] - api_data['price'] * int(request.form.get("shares"))
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_updated, session["user_id"])
        flash("Bought!")
        return redirect("/")

    else:
        return render_template("/buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    table_data = db.execute("SELECT symbol, shares, transaction_type, price, transaction_time FROM transactions WHERE id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?)", session["user_id"])

    return render_template("/history.html", table_data=table_data)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        api_data = lookup(request.form.get("symbol"))
        if api_data == None:
            return apology("provide a valid symbol")

        return render_template("/quoted.html", api_data=api_data)

    else:
        return render_template("/quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif not request.form.get("confirmation"):
            return apology("must confirm password")
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password doesn't match")
        else:
            row = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            if len(row) != 0:
                return apology("user already exists")

        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"))
        user_id = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)
        flash("Registered!")
        session["user_id"] = user_id
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        return render_template("/index.html",  total=cash[0]['cash'], cash=cash[0]['cash'])

    else:
        return render_template("/register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    symbols = db.execute("SELECT DISTINCT(symbol) FROM transactions WHERE transaction_type = 'buy' AND id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?) ORDER BY symbol", session["user_id"])
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("select a symbol")
        elif not request.form.get("shares").isdigit():
            return apology("provide a valid number")

        for i in range(len(symbols)):
            if symbols[i]['symbol'] == request.form.get("symbol"):
                shares_bought = db.execute("SELECT SUM(shares) FROM transactions WHERE transaction_type = 'buy' AND symbol = ? AND id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?)", request.form.get("symbol"), session["user_id"])
                shares_sold = db.execute("SELECT SUM(shares) FROM transactions WHERE transaction_type = 'sell' AND symbol = ? AND id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?)", request.form.get("symbol"), session["user_id"])
                if (shares_sold[0]['SUM(shares)'] != None and (shares_sold[0]['SUM(shares)'] + int(request.form.get("shares"))) > shares_bought[0]['SUM(shares)']) or int(request.form.get("shares")) > shares_bought[0]['SUM(shares)']:
                    return apology("can't afford")

                api_data = lookup(request.form.get("symbol"))
                cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
                transaction_id = db.execute("INSERT INTO transactions (symbol, company, shares, price, transaction_type) VALUES (?, ?, ?, ?, ?)", api_data['symbol'], api_data['name'], int(request.form.get("shares")), api_data['price'], 'sell')
                db.execute("INSERT INTO users_transactions (user_id, transaction_id) VALUES (?, ?)", session["user_id"], transaction_id)
                cash_updated = cash[0]['cash'] + api_data['price'] * int(request.form.get("shares"))
                db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_updated, session["user_id"])
                flash("Sold!")
                return redirect("/")

        return apology("meow! I'll bite..")

    else:
        for i in range(len(symbols) - 1, -1, -1):
            shares_bought = db.execute("SELECT SUM(shares) FROM transactions WHERE transaction_type = 'buy' AND symbol = ? AND id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?)", symbols[i]['symbol'], session["user_id"])
            shares_sold = db.execute("SELECT SUM(shares) FROM transactions WHERE transaction_type = 'sell' AND symbol = ? AND id IN (SELECT transaction_id FROM users_transactions WHERE user_id = ?)", symbols[i]['symbol'], session["user_id"])
            if shares_bought[0]['SUM(shares)'] == shares_sold[0]['SUM(shares)']:
                symbols.pop(i)

        return render_template("/sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
