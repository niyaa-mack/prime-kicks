from flask import Flask, render_template, request, flash

import pymysql

from dynaconf import Dynaconf

from flask import request, redirect, url_for, render_template

config = Dynaconf(settings_file=["settings.toml"])

app = Flask(__name__)

app.secret_key = config.secret_key 

users = []

def connect_db():
    conn = pymysql.connect(
        host="db.steamcenter.tech", 
        user="smack",
        password=config.password,
        database="smack_prime_kicks",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

    return conn

@app.route("/home")
def index():
    return render_template("homepage.html.jinja")

@app.route("/browse")
def browse():
    connection = connect_db()

    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM `Product`")

    result = cursor.fetchall()

    connection.close()

    return render_template("browse.html.jinja", products=result)

@app.route("/product/<product_id>")
def product_page(product_id):
    connection = connect_db()

    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM `Product` WHERE `ID` = %s", (product_id))

    result = cursor.fetchone()

    connection.close()

    return render_template("product.html.jinja", product=result)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "password":
            return redirect(url_for("index"))
        
        else:
            return render_template("login.html.jinja",
                                error="Invalid username or password")

    return render_template("login.html.jinja")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':   
        name = request.form['name']

        email = request.form['email']

        password = request.form['password']

        confirm_password = request.form['confirm_password']

        address = request.form['address']

        if password != confirm_password:
            flash("Passwords don't match")
        elif len(password) < 8:
            flash("password is too short ")
        else:
            connection = connect_db()
            
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO `User` ( `Name`, `Email`, `Password`, `Address` )
                VALUES (%s, %s, %s, %s )
            """, (name, email, password, address) )

            return redirect(/'login.html.jinja')

    return render_template('signup.html.jinja')