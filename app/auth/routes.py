from app import db
from flask import flash, redirect, render_template, request, url_for, \
                  current_app, session
from flask_login import current_user, login_required, login_user, logout_user
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, PasswordChangeForm, \
                           PasswordResetRequestForm, PasswordResetForm,\
                           UserUpdateForm
from app.main.forms import ProviderSearchForm
from app.models import User, Address
from app.helpers import dbAdd, dbUpdate, pagination_urls, email_verified
from werkzeug.urls import url_parse

@bp.route('/')
@bp.route('/index')
@email_verified
def index():
    logged_in = current_user.is_authenticated
    if current_user.is_authenticated:
        user = current_user
        form = ProviderSearchForm(obj=current_user.address)
        form.state.data = current_user.address.state.id
        return render_template("index.html", user=user, form=form,
                               title="Search", logged_in=logged_in)
    else:
        form = LoginForm()
        return render_template("auth/welcome.html", form=form, title="Welcome")

@bp.route('/emailverify/<token>')
def email_verify(token):
    user, error = User.verify_email_verification_token(token)
    if not user:
        if error == "Expired":
            msg = "Email verification failed due to expiration of verification "\
                  "code.  Please login and request a new verification code."
        else:
            msg = "Email verification failed.  Please login and request a new "\
                  "verification code to try again." 
    else:
        user.email_verified = True
        dbUpdate()
        msg = "Email successfully verified."
    flash(msg)
    return redirect(url_for('auth.index'))

@bp.route('/emailverifyrequest')
def email_verify_request():
    if not current_user.is_authenticated:
        flash("Please log in to request a new email verification link.")
        return redirect(url_for("auth.index"))
    else:
        current_user.send_email_verification()
        session['email_verification_sent'] = True
        flash("Please check your email for an email verification message.")
        return redirect(request.referrer)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.index"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("auth.index")
        return redirect(next_page)
    return render_template("auth/welcome.html", title="Sign In", form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))


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
        return redirect(url_for('auth.index'))
    return render_template('auth/password_reset_request.html',
                          title="Password Reset", form=form)


@bp.route('/passwordreset/<token>', methods=['GET', 'POST'])
def passwordreset(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    user = User.verify_password_reset_token(token)
    if not user:
        return redirect(url_for('auth.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password_new.data)
        db.session.commit()
        flash("Your password has been reset.")
        return redirect(url_for('auth.index'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/passwordupdate', methods=['POST'])
@login_required
@email_verified
def passwordupdate():
    pform = PasswordChangeForm()
    if pform.validate_on_submit():
        current_user.set_password(pform.new.data)
        dbUpdate()
        flash("Password updated")
        return redirect(url_for('main.user', username=current_user.username))
    form = UserUpdateForm()
    modal_title = "Edit User Information"
    modal_title_2 = "Change Password"
    pword_open = True
    flash("Password update failed, please correct errors")
    page = request.args.get('page', 1, int)
    user = current_user
    reviews = user.profile_reviews().paginate(page,
                                              current_app.config["REVIEWS_PER_PAGE"],
                                              False)
    summary = user.summary()
    pag_args = {"username": user.username}
    pag_urls = pagination_urls(reviews, 'main.user', pag_args)
    return render_template("user.html", title="User Profile", user=user,
                           reviews=reviews.items, form=form,
                           modal_title=modal_title, pform=pform, 
                           modal_title_2=modal_title_2, pword_open=pword_open,
                           pag_urls=pag_urls, summary=summary)



@bp.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        address = Address(line1=form.address.line1.data, 
                          line2=form.address.line2.data, 
                          city=form.address.city.data, 
                          state_id=form.address.state.data,
                          zip=form.address.zip.data)
        user = User(first_name=form.first_name.data, 
                    last_name=form.last_name.data, email=form.email.data, 
                    username=form.username.data, address=address)
        user.set_password(form.password.data)
        dbAdd(user)
        user.send_email_verification()
        session['email_verification_sent'] = True
        flash("Please check your email for an email verification message.")
        flash("Congratulations! You've successfully registered.")
        return redirect(url_for('auth.index'))
    return render_template("auth/register.html", title='Register', form=form)

    
@bp.route('/userupdate', methods=["POST"])
@login_required
@email_verified
def userupdate():
    """Update user information minus password which is updated seperately."""
    form = UserUpdateForm()
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
        dbUpdate()
        current_user.send_email_verification()
        flash("User information updated")
        return redirect(url_for('main.user', username=current_user.username))
    # re-render page if form not validated
    modal_title = "Edit User Information"
    modal_open = True
    flash("User information update failed.  Please correct errors.")
    page = request.args.get('page', 1, int)
    user = current_user
    reviews = user.profile_reviews().paginate(page, current_app.config["REVIEWS_PER_PAGE"], False)
    summary = user.summary()
    pag_args = {"username": user.username}
    pag_urls = pagination_urls(reviews, 'main.user', pag_args)
    return render_template("user.html", form=form, reviews=reviews.items,
                           title="User Profile", modal_title=modal_title, 
                           user=user, modal_open=modal_open, pag_urls=pag_urls,
                           summary=summary)