from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

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
    """Generates and handles registration submission"""

    if 'username' in session:
        flash("You'll need to log out to view that page.", "text-danger")
        return redirect(f"/users/{session['username']}")

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
        flash('Welcome! Successfully Created Your Account!', "text-success")
        return redirect(f"/users/{new_user.username}")

    return render_template('register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Generates and handles login form submission"""
    if 'username' in session:
        flash("You'll need to log out to view that page.", "text-danger")
        return redirect(f"/users/{session['username']}")

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
def show_user(username):
    """Displays user information"""
    form = DeleteForm()
    # if 'username' not in session:
    #     flash("Please login first!", "text-danger")
    #     return redirect('/login')

    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)

    return render_template('user-details.html', user=user, form=form)

@app.route("/logout")
def logout():
    """Logs out user"""
    session.pop('username')

    return redirect('/')

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Deletes signed in user from db"""

    #Check that user signed in is the same as the user being deleted
    # if session['username'] != username:
    #     flash("You do not have permission to delete that user. Please sign in to the account you wish to delete.", "text-danger")
    #     return redirect('/login')

    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)

    db.session.delete(user)
    db.session.commit()

    return redirect('/logout')

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Generates form to submit additional feedback and handles submission for signed in user"""

    #Check that user signed in is the same as the user being deleted
    # if session['username'] != username:
    #     flash("You do not have permission to add feedback as that user. Please sign in to the account you wish to add feedback for.", "text-danger")
    #     return redirect('/login')

    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        #Don't need to except integrity errors since username is checked above
        db.session.commit()

        flash('Thanks! Your feedback has been added.', "text-success")
        return redirect(f"/users/{username}")

    return render_template('add-feedback.html', form=form)

@app.route("/feedback/<int:feedback_id>/update", methods = ["GET", "POST"])
def update_feedback(feedback_id):
    """Generates and handles form submission to update feedback for signed in user"""

    feedback = Feedback.query.get(feedback_id)
    user = feedback.user

    #Check that user signed in is the same as the user being deleted
    # if session['username'] != user.username:
    #     flash("You do not have permission to update feedback as that user. Please sign in to the account you wish to update feedback for.", "text-danger")
    #     return redirect('/login')

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()
    if form.validate_on_submit():

        title = form.title.data
        content = form.content.data

        feedback.title = title
        feedback.content = content

        db.session.commit()

        flash('Thanks! Your feedback has been updated.', "text-success")
        return redirect(f"/users/{feedback.username}")

    return render_template("update-feedback.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Deletes signed in user's feedback from db"""

    feedback = Feedback.query.get(feedback_id)

    #Check that user signed in is the same as the user being deleted
    # if session['username'] != feedback.username:
    #     flash("You do not have permission to delete that feedback for that user. Please sign in to the account you wish to delete feedback for.", "text-danger")
    #     return redirect('/login')

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()
    
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    flash("Your feedback has been deleted.", "text-success")
    return redirect(f"/users/{feedback.username}")