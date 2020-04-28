from flask import flash, redirect, render_template, url_for, \
                  current_app, request, jsonify, json
from flask_login import current_user, login_required

from app.models import Message, Message_User
from app.message import bp
from app.message.forms import ContactMessageForm, UserMessageForm
from app.utilities.email import send_email
from app.utilities.helpers import save_url
from app.utilities.pagination import Pagination


@bp.route('/about')
def about():
    return render_template("message/about.html", title="About")


@bp.route('/message/contact_us', methods=['GET', 'POST'])
def contactMessage():
    form = ContactMessageForm()
    form = form.initialize_fields(current_user)
    if form.validate_on_submit():
        recipients = current_app.config.get('ADMINS')
        sender = 'no-reply@' + current_app.config['MAIL_SERVER']
        subject = f"{form.category.data} / {form.subject.data}"
        text = render_template("message/email/contactMessage.txt", form=form)
        send_email(subject, sender, recipients, None, text, None)
        flash("Message sent.")
        return redirect(url_for('auth.welcome'))
    if current_user.is_authenticated and request.method == 'GET':
        form = form.initialize_values(current_user)
    return render_template(
        'message/contact_message.html', title="Contact Us", form=form
        )


@bp.route('/message/send', methods=["POST"])
@login_required
def send_message():
    """send message to another user"""
    form = UserMessageForm()
    if form.validate_on_submit():
        message_id = form.message_user_id.data
        if message_id == "" or message_id is None:
            Message.send_new(
                sender_dict=dict(user_id=current_user.id),
                recipient_dict=dict(user_id=form.recipient_id.data),
                subject=form.subject.data,
                body=form.body.data
            )

        else:
            existing_message = Message_User.query.get(message_id).message
            existing_message.send_reply(
                subject=form.subject.data,
                body=form.body.data
            )
        return jsonify(dict(status="success"))
    return jsonify(
        dict(
            status="failure",
            errorMsg=form.errors
        )
    )


@bp.route('/message/<folder>', methods=['GET'])
@login_required
@save_url
def view_messages(folder):
    messages = current_user.get_messages(folder)
    page = request.args.get('page', 1, int)
    pagination = Pagination(messages, page, current_app.config.get('PER_PAGE'))
    pag_urls = pagination.get_urls('message.view_messages', dict(folder=folder))
    messages = pagination.paginatedData
    new_message = UserMessageForm()
    messages_dict = [{"id": msg.id,
                      "timestamp": msg.message.timestamp,
                      "read": msg.read,
                      "sender_id": msg.message.sender.user_id,
                      "sender_full_name": msg.message.sender.full_name,
                      "sender_user_name": msg.message.sender.user.username,
                      "status": msg.tag,
                      "subject": msg.message.subject,
                      "body": msg.message.body} for msg in messages]
    messages_json = json.dumps(messages_dict)
    pagination_json = json.dumps(pag_urls)
    return render_template(
        "messages.html", title="messages", messages=messages,
        pagination_json=pagination_json, new_message=new_message,
        messages_json=messages_json
    )


@bp.route('/message/update/read', methods=["POST"])
@login_required
def message_update_read():
    """update message as having been read."""
    msg = Message_User.query.get(request.form.get('id'))
    if msg is not None and msg.user_id == current_user.id:
        msg.update(read=True)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})


@bp.route('/message/move', methods=['POST'])
@login_required
def move_message():
    message_ids = request.form.get('message_id').split(',')
    tag = request.form.get('tag')
    flash_status = {
        'trash': 'deleted',
        'archive': 'archived',
        'inbox': 'moved to inbox'
    }
    if tag not in ['trash', 'archive', 'inbox']:
        flash("Invalid request.  Please choose a valid folder.")
    else:
        moved = []
        for id in message_ids:
            msg = Message_User.query.get(id)
            if msg is not None and msg.user_id == current_user.id:
                msg.update(tag=tag)
                moved.append(True)
        if len(moved) == 1:
            flash(f"Message {flash_status[tag]}.")
        elif len(moved) > 1:
            flash(f"Messages {flash_status[tag]}.")
        else:
            flash("Unable to move message(s). Please try again.")
    return redirect(url_for('message.view_messages', folder="inbox"))


@bp.route('/message/unread_count')
@login_required
def get_message_unread_count():
    count = current_user.get_inbox_unread_count()
    return jsonify({'unread_count': count})
