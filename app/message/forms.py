from flask_login import current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SelectField, SubmitField, TextAreaField,\
                    HiddenField, IntegerField
from wtforms.validators import (InputRequired, Email, AnyOf, Optional,
                                ValidationError, Length)

from app.models import User, Message_User


class ContactMessageForm(FlaskForm):
    """Collects information to register new user for site.

    Fields:
        sender_id (int): id of user if authenticated
        first_name (str): User first name
        last_name (str): User last name
        email (str): User email address
        category (list): list of categories why user is contacting us
        subject (str): subject of message
        body (text): text body of message
    """
    url = HiddenField("Url", validators=[AnyOf(["", None], message='')])
    sender_id = HiddenField(
        "Sender_ID",
        render_kw={
            'readonly': True
        },
    )
    first_name = StringField(
        "First Name",
        validators=[InputRequired(message="First name is required.")]
    )
    last_name = StringField(
        "Last Name",
        validators=[InputRequired(message="Last name is required.")]
    )
    email = StringField(
        "Email Address",
        validators=[
            InputRequired(message="Email address is required."),
            Email()
        ]
    )
    category = SelectField(
        "Category",
        choices=[
            ('question', 'Ask us a question'),
            ('suggestion', 'Give us a suggestion'),
            ('problem', 'Report a problem')
        ],
        validators=[InputRequired(message="Category is required.")]
    )
    subject = StringField(
        "Subject",
        validators=[InputRequired(message="Subject is required.")]
    )
    body = TextAreaField(
        "Message Body",
        render_kw={"rows": 6},
        validators=[InputRequired(message="Message body is required.")]
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit")

    def validate_sender_id(self, sender_id):
        """validates id matches submitted name and email address."""
        if not current_user.is_authenticated:
            pass
        elif sender_id.data is None or sender_id.data == "":
            raise ValidationError("Sender id is required.")
        else:
            sender = User.query.get(sender_id.data)
            if sender is None:
                raise ValidationError("Invalid Sender")

    def initialize_fields(self, current_user):
        if current_user.is_authenticated:
            self.first_name.render_kw = dict(readonly=True)
            self.last_name.render_kw = dict(readonly=True)
            delattr(self, 'email')
        else:
            delattr(self, 'sender_id')
        return self

    def initialize_values(self, current_user):
        if current_user.is_authenticated:
            self.sender_id.data = current_user.id
            self.first_name.data = current_user.first_name
            self.last_name.data = current_user.last_name
        else:
            delattr(self, 'id')
        return self


class UserMessageForm(FlaskForm):
    """Form for users to send each other messages."""
    recipient_id = IntegerField(
        "to_id", id="msg_new_recipient_id",
        render_kw={
            "readonly": True, "hidden": True
        },
        validators=[InputRequired("Recipient ID is required.")]
    )
    message_user_id = IntegerField(
        "message_user_id", id="message_user_id",
        render_kw={
            "readonly": True, "hidden": True
        },
        validators=[Optional(strip_whitespace=True)]
    )
    recipient = StringField(
        "To", id="msg_new_recipient",
        render_kw={
            "readonly": True
        },
        validators=[InputRequired("Recipient is required.")]
    )
    subject = StringField("Subject", id="msg_new_subject")
    body = TextAreaField(
        "Message Body", render_kw=dict(rows=6), id="msg_new_body",
        validators=[Length(min=0, max=1000)]
    )
    submit = SubmitField("Send", id="submit_msg")

    def validate_recipient_id(self, recipient_id):
        recipient = User.query.filter_by(id=recipient_id.data).first()
        if recipient is None:
            raise ValidationError(
                f"User ({self.recipient.data}) does not exist."
            )

    def validate_message_user_id(self, message_user_id):
        id = message_user_id.data
        if id is None:
            pass
        else:
            message = Message_User.query.get(id).message
            if message is None or message.recipient.user_id != current_user.id:
                raise ValidationError(
                    "Not a valid message to reply to. Please refresh and try"
                    " again."
                )
