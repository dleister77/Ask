from flask import flash, redirect, render_template, url_for, \
                  current_app, request
from flask_login import current_user

from app.admin import bp
from app.admin.forms import MessageForm
from app.utilities.email import send_email


@bp.route('/about')
def about():
    return render_template("admin/about.html", title="About")


@bp.route('/contact/message', methods=['GET', 'POST'])
def contactMessage():
    form = MessageForm()
    form = form.initialize_fields(current_user)
    if form.validate_on_submit():
        recipients = current_app.config.get('ADMINS')
        sender = 'no-reply@' + current_app.config['MAIL_SERVER']
        subject = f"{form.category.data} / {form.subject.data}"
        text = render_template("admin/email/contactMessage.txt", form=form)
        send_email(subject, sender, recipients, None, text, None)
        flash("Message sent.")
        return redirect(url_for('auth.welcome'))
    if current_user.is_authenticated and request.method == 'GET':
        form = form.initialize_values(current_user)
    return render_template(
        'admin/contactMessage.html', title="Contact Us", form=form
        )
