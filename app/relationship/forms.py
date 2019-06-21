from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, HiddenField)
from wtforms.validators import DataRequired, ValidationError
from app.models import User, Group


def unique_check(modelClass, columnName):
    """validate that no other entity in class registered for field.
    inputs:
        modelClass: db model class to query
        columnName: db column in modelclass.columname format
    """
    
    def _unique_check(form, field):
        key = {"email": "Email address",
               "telephone": "Telephone number",
               "name":"Name"}
        message = f"{key[field.name]} is already registered."
        entity = modelClass.query.filter(columnName == field.data).first()
        if entity is not None:
            raise ValidationError(message)
    return _unique_check

def exists_check(modelClass):
    """validate that item being added as relationship already exists.
    inputs:
        modelClass: db model class of item being added
    """
    def _exists_check(form, field):
        new = modelClass.query.filter_by(id=field.data).first()
        msg_dict = {"Group": "group", "User": "person"}
        key = modelClass.__name__
        message = f"{msg_dict[key].capitalize()} does not exist, please choose a different {msg_dict[key]} to add."
        if new is None:
            raise ValidationError(message)
    return _exists_check

def relation_check(relationshipType):
    """validate that not already in relation with item being added.
    Inputs:
        relationshipType: relationship being checked on user (i.e. groups or 
        friends)
        """
    message_dict = {"friends":"You are already friends with this person.", 
                    "groups":"You are already a member of this group.",
                    "self": "You are naturally friends with yourself.  No need to add to friend network."}
    model_dict = {"friends":User, "groups":Group}

    def _relation_check(form, field):   
        relation = (model_dict[relationshipType].query.filter_by(id=field.data)
                                               .first())
        relation_list = getattr(current_user, relationshipType)
        if relation == current_user:
            raise ValidationError(message_dict["self"])
        elif relation in relation_list:
            raise ValidationError(message_dict[relationshipType])
    return _relation_check

class GroupSearchForm(FlaskForm):
    """Form to search for group."""
    name = StringField("Group Name", id="group_name", validators=[DataRequired(message="Group name is required.")])
    value = HiddenField("Group Value", id="group_value", validators=
                        [DataRequired(message="Group name is required."), exists_check(Group), relation_check("groups")])
    submit = SubmitField("Add Group", id="submit-group-add")


class FriendSearchForm(FlaskForm):
    """Form to search for group."""
    name = StringField("Friend Name", id="friend_name", 
                       validators=[DataRequired(message="Name is required.")])
    value = HiddenField("Friend Value", id="friend_value", validators=
                        [DataRequired("Name is required."), relation_check("friends")])
    submit = SubmitField("Add Friend", id="submit-friend-add")


class GroupCreateForm(FlaskForm):
    """Form to create new group."""
    name = StringField("Group Name", validators=[DataRequired(message="Group name is required."),
                       unique_check(Group, Group.name)])
    description = TextAreaField("Description", validators=[DataRequired("Description is required.")])
    submit = SubmitField("Add Group", id="submit_new_group")

class GroupEditForm(GroupCreateForm):
    """Form to edit existing group."""
    name = StringField("Group Name", validators=[DataRequired(
                                     message="Group name is required.")])
    submit = SubmitField("Update Group", id="update_group")
    id = HiddenField("Group ID", id="group_id", validators=
                        [DataRequired("Group name is required.")])
    def validate_id(self, id):
        g = Group.query.filter_by(id=self.id.data).first()
        if not g:
            raise ValidationError("Invalid update. Group does not exist. Refresh and try again.")
    
    def validate_name(self, name):
        """Check if new name not equal to another group."""
        g = Group.query.filter_by(name=self.name.data).first()
        existing = Group.query.filter_by(id=self.id.data).first()
        if g is not None and g != existing:
            raise ValidationError("Group name is already registered.")