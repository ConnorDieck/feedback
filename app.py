from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route("/")
def show_home():
    """Redirects to home page"""

    return redirect('/register')

@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')    
            return render_template('register.html', form=form)

        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f"/users/{new_user.username}")

    return render_template('register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.first_name}!", "text-primary")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route("/users/<username>")
def show_secret(username):
    if 'username' not in session:
        flash("Please login first!", "text-danger")
        return redirect('/login')

    user = User.query.get(username)

    return render_template('user-details.html', user=user)

@app.route("/logout")
def logout():
    session.pop('username')

    return redirect('/')

@app.route("/users/<username>/delete")
def delete_user(username):
    if session['username'] is not username:
        flash("Please login as the correct user first!", "text-danger")
        return redirect('/login')

    user = User.query.get(username)

    db.session.delete(user)
    db.session.commit()
