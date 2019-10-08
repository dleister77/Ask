from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,SubmitField, TextAreaField
from wtforms.validators import (InputRequired, Email)
                                
class MessageForm(FlaskForm):
    """Collects information to register new user for site.

    Fields:
        first_name (str): User first name
        last_name (str): User last name
        email (str): User email address
        category (list): list of categories why user is contacting us
        subject (str): subject of message
        body (text): text body of message
    """

    first_name = StringField("First Name", validators=[InputRequired(message="First name is required.")])
    last_name = StringField("Last Name", validators=[InputRequired(message = "Last name is required.")])
    email = StringField("Email Address", validators=[InputRequired(message="Email address is required."), Email()])
    category = SelectField("Category", choices=[('question', 'Ask us a question'),
                                                ('suggestion', 'Give us a suggestion'),
                                                ('problem', 'Report a problem')],
                        validators=[InputRequired(message="Category is required.")])
    subject = StringField("Subject", validators=[InputRequired(message="Subject is required.")])
    message = TextAreaField("Message", render_kw = {"rows": 6}, validators=[InputRequired()])
    submit = SubmitField("Submit")
    
