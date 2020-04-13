from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField,\
                    HiddenField
from wtforms.validators import (InputRequired, Email, AnyOf, Optional,
                                ValidationError)

from app.models import User


class MessageForm(FlaskForm):
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
