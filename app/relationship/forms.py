from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, ValidationError

from app.models import FriendRequest, Group, GroupRequest, User
from app.utilities.forms import MultiCheckboxField


def unique_check(modelClass, columnName):
    """validate that no other entity in class registered for field.

    Factory function.  Returns callable validator to verify value being added
    is unique to that entity

    Args:
        modelClass (class): db model class to query (i.e. User)
        columnName: db column in modelclass.columname format (i.e. User.email)

    Returns:
        _unique_check(function)

    Raises:
       ValidationError: if value (i.e. email address) already in use by another
       entity
    """

    def _unique_check(form, field):
        key = {
            "email": "Email address",
            "telephone": "Telephone number",
            "name": "Name"
        }
        message = f"{key[field.name]} is already registered."
        entity = modelClass.query.filter(columnName == field.data).first()
        if entity is not None:
            raise ValidationError(message)
    return _unique_check


def exists_check(modelClass):
    """validate that item being added as relationship already exists.

    Factory function.  Returns callable validator to verify entity being added
    exists

    Args:
        modelClass(Class): db model class (Group or User) of entity being added
        as relation

    Returns:
        _exists_check (function)

    Raises:
        ValidationError: If group or user does not exist

    """
    def _exists_check(form, field):
        new = modelClass.query.filter_by(id=field.data).first()
        msg_dict = {"Group": "group", "User": "person"}
        key = modelClass.__name__
        message = (f"{msg_dict[key].capitalize()} does not exist, please"
                   f" choose a different {msg_dict[key]} to add.")
        if new is None:
            raise ValidationError(message)
    return _exists_check


def relation_check(relationshipType):
    """validate that not already in relation with item being added.

    Factory function.  Returns callabled validator which checks if current user
        is already in passed in relationship type with entity being added

    Args:
        relationshipType: relationship being checked on user (i.e. groups or
        friends)

    Returns:
        _relation_check(function)

    Raises:
        ValidationError: if entity being added is oneself or if already in
        relation

    """

    message_dict = {
        "friends": "You are already friends with this person.",
        "groups": "You are already a member of this group.",
        "self": "You are naturally friends with yourself.  No need to add to"
                " friend network."
    }
    model_dict = {
        "friends": User, "groups": Group
    }

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
    """Form to search for group.

    Fields:
        name (str): name of group being searched
    """
    class Meta:
        csrf = False

    name = StringField(
        "Group Name", id="group_name",
        validators=[InputRequired(message="Group name is required.")]
    )
    submit = SubmitField("Search for Group", id="submit-group-add")


class GroupAddForm(FlaskForm):
    """Hidden form to add group.via join button

    Fields:
        id (int): id of group being searched
    """

    id = HiddenField(
        "Group Name",
        validators=[
            InputRequired(message="Do not disable hidden fields."),
            exists_check(Group)
        ]
    )
    submit = SubmitField("Join")


class FriendApproveForm(FlaskForm):
    """Form to select friends to delete.

    Fields:
        name (checkbox): received friend request to approve, displays full
        name.  value corresponds to request id.

    Methods:
        validate_name: checks that friend request exists and is in user's list
            of outstanding friend requests
        populate_choices: populates check box name/value pairs for users's
            outstanding friend requests.
    """

    name = MultiCheckboxField(
        "Received - select and submit to approve", coerce=int,
        render_kw={"class": "nobullets"},
        validators=[
            InputRequired(
                message="Please select at least one name to approve.")
            ]
    )
    submit = SubmitField("Submit", id="friend_approve")

    def validate_name(self, name):
        """verify request being approved is valid."""
        for id in self.name.data:
            friendrequest = FriendRequest.query.get(id)
            if (friendrequest is None or friendrequest not in
               current_user.receivedfriendrequests):
                raise ValidationError("Please select name from the list.")

    def populate_choices(self, user):
        """Populates name/value pairs for user's friend request approval list.

        Args:
            user (User): User whose request list is being generated.

        Returns:
            self

        """
        if len(user.receivedfriendrequests) > 0:
            choices = [(request.id, request.requestor.full_name) for request in
                       user.receivedfriendrequests]
        else:
            choices = []
        self.name.choices = choices
        return self


class FriendDeleteForm(FlaskForm):
    """Form to select friends to delete.

    Fields:
        name (checkbox): List of friends available to delete.  Displays full
            name and sets value equal to friend's id

    Methods:
        validate_name: checks that name being deleted is actual user and is in
            current user's friend list prior to deletion
        populate_choices: populates checkbox name/value list with
            full name/userid of each friend available for deletion
    """
    name = MultiCheckboxField(
        "Select friends to remove", render_kw={"class": "nobullets"},
        coerce=int,
        validators=[
            InputRequired(message="At least one name must be selected.")
        ]
    )
    submit = SubmitField("Submit", id="friend_delete")

    def validate_name(self, name):
        """verfiy name being deleted exists and is in user's friend list."""
        for friend_id in self.name.data:
            f = User.query.get(friend_id)
            if f is None or f not in current_user.friends:
                raise ValidationError("Please select friend from list.")

    def populate_choices(self, user):
        """Populates name/value pairs for user's friend delete list list.

        Args:
            user (User): User whose request list is being generated.

        Returns:
            self

        """
        if len(user.friends) > 0:
            choices = [
                (friend.id, friend.full_name) for friend in user.friends
            ]
        else:
            choices = []
        self.name.choices = choices
        return self


class FriendSearchForm(FlaskForm):
    """Form to search for group.

    Fields:
        name (str): full name (first and last) of friend being searched
        id (int): hidden, id of friend being added.

    """

    name = StringField(
        "Friend Name", id="friend_name",
        validators=[InputRequired(message="Name is required.")]
    )
    id = HiddenField(
        "Friend ID", id="friend_value",
        validators=[
            InputRequired("Name is required."), exists_check(User),
            relation_check("friends")
        ]
    )
    submit = SubmitField("Add Friend", id="submit-friend-add")


class GroupCreateForm(FlaskForm):
    """Form to create new group.

    Fields:
        id (int): hidden, id of group being edited.
        name (str): Name of group
        description (str): from GroupCreate, short description of group

    """
    name = StringField(
        "Group Name",
        validators=[
            InputRequired(message="Group name is required."),
            unique_check(Group, Group.name)
        ]
    )
    description = TextAreaField(
        "Description", render_kw={"rows": 3},
        validators=[InputRequired("Description is required.")]
    )
    submit = SubmitField("Add Group", id="submit_new_group")


class GroupDeleteForm(FlaskForm):
    """Form to select groups to exit.

    Fields:
        name (checkbox): List of groups available to delete.  Displays full
            name and sets value equal to group's id

    Methods:
        validate_name: checks that name being deleted is actual group and is in
            current user's group list prior to deletion
        populate_choices: populates checkbox name/value list with
            group name/id of each friend available for deletion
    """

    name = MultiCheckboxField(
        "Select groups to remove", render_kw={"class": "nobullets"},
        coerce=int,
        validators=[
            InputRequired(message="At least one group must be selected.")
        ]
    )
    submit = SubmitField("Submit", id="group_delete")

    def validate_name(self, name):
        """verfiy name being deleted exists and is in user's group list."""
        for group_id in self.name.data:
            group = Group.query.get(group_id)
            if group is None or group not in current_user.groups:
                raise ValidationError("Please select a group from the list.")

    def populate_choices(self, user):
        """Generate list of tuples containing group's id and name.

        Args:
            user (User): User whose list is being generated.

        Returns:
            self
        """

        if len(user.groups) > 0:
            choices = [(group.id, group.name) for group in user.groups]
        else:
            choices = []
        self.name.choices = choices
        return self


class GroupEditForm(GroupCreateForm):
    """Form to edit existing group.

    Fields:
        id (int): hidden, id of group being edited.
        name (str): Name of group
        description (str): from GroupCreate, short description of group
    Methods:
        validate_id: checks that id matches existing group
        validate_name: checks that group name and id match and that name does
           not match existing group

    """
    name = StringField(
        "Group Name",
        validators=[InputRequired(message="Group name is required.")]
    )
    submit = SubmitField("Update Group", id="update_group")
    id = HiddenField(
        "Group ID", id="group_id", render_kw={"readonly": True},
        validators=[
            InputRequired("Group ID is required.  Please do not remove.")
        ]
    )

    def validate_id(self, id):
        g = Group.query.filter_by(id=self.id.data).first()
        if not g:
            raise ValidationError(
                "Invalid update. Group does not exist. Refresh and try again."
            )

    def validate_name(self, name):
        """Check if new name not equal to another group."""
        g = Group.query.filter_by(name=self.name.data).first()
        existing = Group.query.filter_by(id=self.id.data).first()
        if g is not None and g != existing:
            raise ValidationError("Group name is already registered.")


class GroupMemberApproveForm(FlaskForm):
    """Form to select friends to delete."""
    request = MultiCheckboxField(
        "Received - select and submit to approve",
        render_kw={"class": "nobullets"}, coerce=int,
        validators=[
            InputRequired(
                message="Please select at least one name to approve."
            )
        ]
    )
    submit = SubmitField("Submit", id="group_approve")

    def validate_request(self, request):
        """verify request exists and is in group's request list."""
        # verify that request exists
        for id in self.request.data:
            request = GroupRequest.query.get(id)
            if request is None:
                raise ValidationError(
                    "Invalid request. Please select request from the list."
                )
            if request.group.admin != current_user:
                raise ValidationError(
                    "User not authorized to approve this request."
                )

    def populate_choices(self, user):
        """Get group admin approval choices for approval form.
        Outputs list of tuples containing request id and
        group name / requestor name."""
        choices = []
        for group in user.group_admin:
            for request in group.join_requests:
                choice = (
                    request.id,
                    f"{request.group.name} - {request.requestor.full_name}"
                )
                choices.append(choice)
        self.request.choices = choices
        return self
