from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db
from app.forms import LoginForm, RegistrationForm, ReviewForm, AddProviderForm
from app.models import User, Address, State
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    return render_template("index.html", user=user, title="home")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        state_id = (State.query.filter(State.name == form.address.state.data)
                    .first().id)
        address = Address(line1=form.address.line1.data, 
                          line2=form.address.line2.data, 
                          city=form.address.city.data, 
                          state_id=state_id, 
                          zip=form.address.zip.data)
        user = User(first_name=form.first_name.data, 
                    last_name=form.last_name.data, email=form.email.data, 
                    username=form.username.data, address=address)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations! You've successfully registered.")
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)

@app.route('/review', methods=["GET", "POST"])
def review():
    form = ReviewForm(request.form)
    modalform=AddProviderForm(request.form)
    return render_template("review.html", title="Review",form=form, 
                           modalform=modalform)
