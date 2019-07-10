from flask import current_app, has_request_context, _request_ctx_stack
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, HiddenField,
                     SelectMultipleField)
from wtforms.validators import DataRequired, ValidationError

from app.models import FriendRequest, Group, GroupRequest, User
from app.utilities.forms import MultiCheckboxField, select_multi_checkbox


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


class FriendApproveForm(FlaskForm):
    """Form to select friends to delete."""
    name = MultiCheckboxField("Received - select and submit to approve", render_kw={"class":"nobullets"}, coerce=int)
    submit = SubmitField("Submit", id="friend_approve")

    def validate_name(self, name):
        """verfiy request being approved is valid and current user request recipient."""
        # verify request is valid
        print(self.name.data, name.data)
        friendrequest = FriendRequest.query.get(self.name.data)
        if friendrequest is None or friendrequest not in current_user.receivedfriendrequests:
            raise ValidationError("Invalid request. Please select request from"
                                  " the list.")

    def populate_choices(self, user):
        if len(user.receivedfriendrequests) > 0:
            choices = [(request.id, request.requestor.full_name) for request in
                       user.receivedfriendrequests]
        else:
            choices = []
        self.name.choices = choices
        return self
    
    
class FriendDeleteForm(FlaskForm):
    """Form to select friends to delete."""
    name = MultiCheckboxField("Select friends to remove",
                              render_kw={"class":"nobullets"}, coerce=int, 
                              validators=[DataRequired()])
    submit = SubmitField("Submit", id="friend_delete")

    def validate_name(self, name):
        """verfiy name being deleted exists and is in user's friend list."""
        for friend_id in self.name.data:
            f = User.query.get(friend_id)
            if f is None or f not in current_user.friends:
                raise ValidationError("Select friend from friend list.")

    def populate_choices(self, user):
        """Generate list of tuples containing friends' id and full name."""
        if len(user.friends) > 0:
            choices = [(friend.id, friend.full_name) for friend in user.friends]
        else:
            choices = []
        self.name.choices = choices
        return self

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


class GroupDeleteForm(FlaskForm):
    """Form to select groups to exit."""
    name = MultiCheckboxField("Select groups to remove", render_kw={"class":"nobullets"}, coerce=int,
                              validators=[DataRequired()])
    submit = SubmitField("Submit", id="group_delete")

    def validate_name(self, name):
        """verfiy name being deleted exists and is in user's group list."""
        for group_id in self.name.data:
            group = Group.query.get(group_id)
            print(f"validating {group}")
            if group is None or group not in current_user.groups:
                raise ValidationError("Select group from friend list.")

    def populate_choices(self, user):
        """Generate list of tuples containing group's id and name."""
        if len(user.groups) > 0:
            choices = [(group.id, group.name) for group in user.groups]
        else:
            choices = []
        self.name.choices = choices
        return self

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
        print(f"Current User {current_user}")
        g = Group.query.filter_by(name=self.name.data).first()
        existing = Group.query.filter_by(id=self.id.data).first()
        if g is not None and g != existing:
            raise ValidationError("Group name is already registered.")


class GroupMemberApproveForm(FlaskForm):
    """Form to select friends to delete."""
    request = MultiCheckboxField("Received - select and submit to approve", render_kw={"class":"nobullets"}, coerce=int)
    submit = SubmitField("Submit", id="group_approve")

    def validate_request(self, request):
        """verf exists and is in group's request list."""
        # verify that request exists
        request = GroupRequest.query.get(self.request.data)
        if request is None:
            raise ValidationError("Invalid request. Please select request from the list.")
        # verify that current user is group admin
        request_admin = request.group.admin
        if request_admin != current_user:
            raise ValidationError("User not authorized to approve this request.")

    def populate_choices(self, user):
        """Get group admin approval choices for approval form.
        Outputs list of tuples containing request id and
        group name / requestor name."""
        choices = []
        for group in user.group_admin:
            for request in group.join_requests:
                choice = (request.id, f"{request.group.name} - {request.requestor.full_name}")
                choices.append(choice)
        self.request.choices = choices
        return self