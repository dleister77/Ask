import json

from flask import flash, redirect, render_template, request, url_for,\
                  current_app, session, abort
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, PasswordChangeForm, \
                           PasswordResetRequestForm, PasswordResetForm,\
                           UserUpdateForm
from app.models import User, Address
from app.utilities.helpers import email_verified, form_to_dict
from app.utilities.pagination import Pagination


@bp.route('/')
@bp.route('/welcome')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    return render_template("auth/welcome.html", form=form, title="Welcome")


@bp.route('/emailverify/<token>')
def email_verify(token):
    user, error = User.verify_email_verification_token(token)
    if not user:
        if error == "Expired":
            msg = ("Email verification failed due to expiration of"
                   " verification code.  Please login and request a new"
                   " verification code.")
        else:
            msg = ("Email verification failed.  Please login and request a new"
                   " verification code to try again.")
    else:
        user.email_verified = True
        user.save()
        msg = "Email successfully verified."
    flash(msg)
    return redirect(url_for('auth.welcome'))


@bp.route('/emailverifyrequest')
def email_verify_request():
    if not current_user.is_authenticated:
        flash("Please log in to request a new email verification link.")
        return redirect(url_for("auth.welcome"))
    else:
        current_user.send_email_verification()
        session['email_verification_sent'] = True
        flash("Please check your email for an email verification message.")
        return redirect(request.referrer)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.welcome"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/welcome.html", title="Sign In", form=form)


@bp.route('/logout')
def logout():
    logout_user()
    keysToRemove = ['location', 'email_verification_sent']
    for key in keysToRemove:
        if key in session:
            session.pop(key)
    return redirect(url_for('auth.welcome'))


@bp.route('/passwordresetrequest', methods=['GET', 'POST'])
def password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.send_password_reset_email()
        flash("Check email for instructions to reset your password.")
        return redirect(url_for('auth.welcome'))
    return render_template('auth/password_reset_request.html',
                           title="Password Reset", form=form)


@bp.route('/passwordreset/<token>', methods=['GET', 'POST'])
def passwordreset(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_password_reset_token(token)
    if not user:
        return redirect(url_for('auth.welcome'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password_new.data)
        user.save()
        flash("Your password has been reset.")
        return redirect(url_for('auth.welcome'))
    if not form.validate():
        flash("Password reset failed.  Please correct errors.")
    return render_template('auth/reset_password.html', form=form)


@bp.route('/passwordupdate', methods=['POST'])
@login_required
@email_verified
def passwordupdate():
    pform = PasswordChangeForm()
    if pform.validate_on_submit():
        current_user.set_password(pform.new.data)
        current_user.save()
        flash("Password updated")
        return redirect(url_for('main.user', username=current_user.username))
    form = UserUpdateForm().populate_choices()
    modal_title = "Edit User Information"
    modal_title_2 = "Change Password"
    pword_open = True
    flash("Password update failed, please correct errors")
    page = request.args.get('page', 1, int)
    user = current_user
    reviews = user.reviews
    summary = user.summary()
    pag_args = {"username": user.username}
    pagination = Pagination(reviews, page, current_app.config.get('PER_PAGE'))
    pag_urls = pagination.get_urls('main.user', pag_args)
    reviews = pagination.paginatedData
    return render_template("user.html", title="User Profile", user=user,
                           reviews=reviews, form=form,
                           modal_title=modal_title, pform=pform,
                           modal_title_2=modal_title_2, pword_open=pword_open,
                           pag_urls=pag_urls, summary=summary)


@bp.route('/register2', methods=["GET", "POST"])
def register2():
    if current_user.is_authenticated:
        flash("You are already registered.")
        return redirect(url_for("main.index"))
    form = RegistrationForm().populate_choices()
    if form.validate_on_submit():
        address = Address(line1=form.address.line1.data,
                          line2=form.address.line2.data,
                          city=form.address.city.data,
                          state_id=form.address.state.data,
                          zip=form.address.zip.data)
        user = User.create(first_name=form.first_name.data,
                           last_name=form.last_name.data,
                           email=form.email.data,
                           username=form.username.data,
                           address=address)
        user.set_password(form.password.data)
        user.send_email_verification()
        session['email_verification_sent'] = True
        flash("Congratulations! You've successfully registered.")
        flash("Please check your email for an email verification message.")
        return redirect(url_for('auth.welcome'))
    return render_template("auth/register.html",
                           title='Register', form=form), 422


@bp.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered.")
        return redirect(url_for("main.index"))
    form = RegistrationForm().populate_choices()
    if request.method == "GET":
        form_values = json.dumps(form_to_dict(form, "values"))
        form_errors = json.dumps(form_to_dict(form, "errors"))
        return render_template("auth/register.html", title='Register',
                               form_values=form_values,
                               form_errors=form_errors)
    if form.validate_on_submit():
        address = Address(line1=form.address.line1.data,
                          line2=form.address.line2.data,
                          city=form.address.city.data,
                          state_id=form.address.state.data,
                          zip=form.address.zip.data)
        user = User.create(first_name=form.first_name.data,
                           last_name=form.last_name.data,
                           email=form.email.data,
                           username=form.username.data,
                           address=address)
        user.set_password(form.password.data)
        user.send_email_verification()
        session['email_verification_sent'] = True
        flash("Congratulations! You've successfully registered.")
        flash("Please check your email for an email verification message.")
        return redirect(url_for('auth.welcome'))
    else:
        form_values = json.dumps(form_to_dict(form, "values"))
        form_errors = json.dumps(form_to_dict(form, "errors"))
        return render_template("auth/register.html", title='Register',
                               form_values=form_values,
                               form_errors=form_errors), 422


@bp.route('/userupdate', methods=["POST"])
@login_required
@email_verified
def userupdate():
    """Update user information minus password which is updated seperately."""
    form = UserUpdateForm().populate_choices()
    if form.validate_on_submit():
        current_user.address.update(line1=form.address.line1.data,
                                    line2=form.address.line2.data,
                                    city=form.address.city.data,
                                    zip=form.address.zip.data,
                                    state_id=form.address.state.data)
        address = current_user.address
        current_user.update(first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            email=form.email.data,
                            username=form.username.data,
                            address=address)
        current_user.send_email_verification()
        flash("User information updated")
        return redirect(url_for('main.user', username=current_user.username))
    modal_title = "Edit User Information"
    modal_open = True
    flash("User information update failed.  Please correct errors.")
    page = request.args.get('page', 1, int)
    reviews = current_user.reviews
    summary = current_user.summary()
    pag_args = {"username": current_user.username}
    pagination = Pagination(reviews, page, current_app.config.get('PER_PAGE'))
    pag_urls = pagination.get_urls('main.user', pag_args)
    reviews = pagination.paginatedData
    return render_template("user.html", form=form, reviews=reviews,
                           title="User Profile", modal_title=modal_title,
                           user=current_user, modal_open=modal_open,
                           pag_urls=pag_urls,
                           summary=summary), 422


@bp.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
