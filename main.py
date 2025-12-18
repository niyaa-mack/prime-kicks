from flask import Flask, render_template, request, flash, abort

from flask_login import LoginManager, login_user, logout_user, login_required

import pymysql

from dynaconf import Dynaconf

from flask import request, redirect, url_for, render_template

config = Dynaconf(settings_file=["settings.toml"])

app = Flask(__name__)

app.secret_key = config.secret_key 

login_manager = LoginManager(app)
login_manager.login_view = '/login'



class User:
    is_authenticated = True
    is_active = True
    is_annoymous = False 

    def __init__(self, result):
        self.name = result['Name']
        self.email = result['Email']
        self.address = result['Address']
        self.id = result['ID']

    def get_id(self):
        return str(self.id)
    
@login_manager.user_loader
def load_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `User` WHERE `ID` = %s ", (user_id) )
    result = cursor.fetchone()
    connection.close()

    if result is None:
        return None
    
    return User(result)


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

    if result is None:
        abort(404)

    return render_template("product.html.jinja", product=result)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        connection = connect_db()

        cursor = connection.cursor()

        cursor.execute(" SELECT * FROM `User` WHERE `Email` = %s " , (email))

        result = cursor.fetchone()

        connection.close()

        if result is None:
            flash("No user found")
        elif password != result["Password"]:
            flash("Wrong password")
        else:
            login_user(User(result))
            return redirect("/browse")

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
        try:
            cursor.execute("""  
                INSERT INTO `User` ( `Name`, `Email`, `Password`, `Address` )
                VALUES (%s, %s, %s, %s )
            """, (name, email, password, address) )
            connection.close()
        except pymysql.err.IntegrityError: 
            flash("This email already has an account")
            connection.close()
        else:
            return redirect('/login.html.jinja')

    return render_template('signup.html.jinja')


@app.route("/settings")
@login_required
def settings():
    pass


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect("/homepage.html.jinja")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():   
    return render_template("dashboard.html.jinja ")


