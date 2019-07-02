from datetime import datetime, date
import re
from string import capwords
from time import time

from flask import current_app, render_template
from flask_login import UserMixin, current_user
import jwt
from sqlalchemy import CheckConstraint, or_, and_
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import Model
from app.extensions import db
from app.utilities.email import send_email



# many to many table linking users with groups
user_group = db.Table('user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


# many to many table linking providers to multiple categories
category_provider_table = db.Table('category_provider', db.Model.metadata,
    db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
    db.Column('provider_id', db.Integer, db.ForeignKey('provider.id')))


# many to many table linking pictures with users with friends
user_friend = db.Table('user_friend', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id')))



class State(Model):
    """States used in db.
    Relationships:
        Parent of: Address
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    state_short = db.Column(db.String(24), index=True)
    addresses = db.relationship("Address", backref="state")

    @staticmethod
    def state_list():
        """Query db to populate state list on forms."""
        if current_app.config['TESTING'] == True:
            list = current_app.config['TEST_STATES']
        else:
            try:
                list = [(s.id, s.name) for s in State.query.order_by("name")]
            except OperationalError:
                list = [(1,"Test")]
        return list

    def __repr__(self):
        return f"<State {self.name}>"


class Address(Model):
    """Addresses used for users and providers.
    Relationships:
        Parent of:
        Child of: State, User, Provider
    """
    id = db.Column(db.Integer, primary_key=True)
    _line1 = db.Column(db.String(128), nullable=False)
    _line2 = db.Column(db.String(128))
    zip = db.Column(db.String(20), index=True, nullable=False)
    _city = db.Column(db.String(64), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                  ondelete="CASCADE"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id",
                                                      ondelete="CASCADE"))
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), nullable=False)

    __table_args__ = (
        CheckConstraint('provider_id IS NOT NULL AND user_id IS NOT NULL',
                        name="chk_address_fks"),
    )


    @hybrid_property
    def line1(self):
        return self._line1

    @line1.setter
    def line1(self, line1):
        if line1 is not None:
            line1 = line1.title()
        self._line1 = line1

    @hybrid_property
    def line2(self):
        return self._line2

    @line2.setter
    def line2(self, line2):
        if line2 is not None:
            line2 = line2.title()
        self._line2 = line2

    @hybrid_property
    def city(self):
        return self._city

    @city.setter
    def city(self, city):
        if city is not None:
            city = city.title()
        self._city = city

    def __repr__(self):
        return f"<Address {self.line1}, {self.city}, {self.state}>"


class User(UserMixin, Model):
    """Creates user class.
    Relationships:
        Parent of: Reviews, Address, FriendRequest
        Child of:
        ManytoMany: Group, User(friends)
    Methods:
        set_password: Store submitted password as hash.
        check_password: Compares hashed submitted password to store password hash.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    _email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(128))
    password_set_date = db.Column(db.Date, index=True)
    _first_name = db.Column(db.String(64), index=True, nullable=False)
    _last_name = db.Column(db.String(64), index=True, nullable=False)

    address = db.relationship("Address", backref="user", lazy=False,
                              uselist=False, passive_deletes=True)
    reviews = db.relationship("Review", backref="user", passive_deletes=True)
    friends = db.relationship("User", secondary=user_friend,
                              primaryjoin=(id == user_friend.c.user_id),
                              secondaryjoin=(id == user_friend.c.friend_id),
                              backref="friends_reverse")
    sentfriendrequests = db.relationship("FriendRequest",
                                     primaryjoin="(User.id == FriendRequest.requestor_id)",
                                     backref="requestor",
                                     passive_deletes=True)
    receivedfriendrequests = db.relationship("FriendRequest",
                                     primaryjoin="(User.id == FriendRequest.friend_id)",
                                     backref="requested_friend",
                                     passive_deletes=True)

    sentgrouprequests = db.relationship("GroupRequest", backref="requestor",
                                        passive_deletes=True)


    @hybrid_property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        if first_name is not None:
            first_name = first_name.title()
        self._first_name = first_name

    @hybrid_property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, last_name):
        if last_name is not None:
            last_name = last_name.title()
        self._last_name = last_name

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if email != self._email:
            self._email = email
        else:
            pass

    def set_password(self, password):
        print("setting pword")
        self.password_hash = generate_password_hash(password)
        self.password_set_date = date.today()
        self.save()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _get_token(self, payload, expiration):
        """Generic function to get token.
        Inputs:
        payload: dict of custom inputs
        expiration: days until expiry
        """
        # convert expiration to seconds
        if expiration is None:
            msg = {}
        else:
            expires_in = expiration * 24 * 60 * 60
            msg = {'exp': time() + expires_in}
        msg.update(payload)
        return jwt.encode(msg, current_app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')
    
    def get_reset_password_token(self):
        """Get password reset token."""
        payload = {'reset_password': self.id}
        expiration = 10/(60*24)  # 10 minutes
        return self._get_token(payload, expiration)

    def send_password_reset_email(self):
        token = self.get_reset_password_token()
        send_email('Ask a Neighbor: Password Reset',
                sender=current_app.config['ADMINS'][0],
                recipients=[self.email],
                text_body=render_template('auth/email/reset_password_msg.txt',
                                            user=self, token=token),
                html_body=render_template('auth/email/reset_password_msg.html',
                                            user=self, token=token))

    @staticmethod
    def verify_password_reset_token(token):
        """Static method to verify password reset token.
        Returns: User based on token id.
        """
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def get_email_verification_token(self):
        """Get jwt token for email address verification."""
        payload = {'verify_email': self.id}
        expiration = 10
        return self._get_token(payload, expiration)

    def send_email_verification(self):
        """Send email to request email verification."""
        token = self.get_email_verification_token()
        send_email('Ask a Neighbor: Email Verification',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[self.email],
                   text_body=render_template('auth/email/verify_email_msg.txt',
                                             user=self, token=token),
                   html_body=render_template('auth/email/verify_email_msg.html',
                                             user=self, token=token))

    @staticmethod
    def verify_email_verification_token(token):
        """Check email verification token and returns user if valid and error
           if invalid."""
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['verify_email']
            user = User.query.get(id)
            error = None
        except jwt.ExpiredSignatureError:
            error = "Expired"
            user = None
        except:
            error = "Invalid"
            user = None
        return (user, error)

    def get_friend_list(self):
        """Generate list of tuples containing friend's id and full name."""
        friend_list = []
        for friend in self.friends:
            friend_list.append((friend.id, friend.full_name))
        return friend_list

    def get_friend_request_token(self, friend, request):
        """Get friend request token.
        Inputs:
        friend: User that friend request is being sent to.
        """

        payload = {"request": request.id}
        expiration = None
        return self._get_token(payload, expiration)

    def send_friend_request(self, friend):
        """Send friend request email and update FriendRequest table."""
        request = FriendRequest(friend_id=friend.id,
                                requestor_id=self.id,
                                date_sent=date.today())
        request.save()
        try:
            token = self.get_friend_request_token(friend, request)
            send_email('Ask a Neighbor: Friend Verification',
                    sender=current_app.config['ADMINS'][0],
                    recipients=[friend.email],
                    text_body=render_template('relationship/email/friend_request.txt',
                                                user=friend, friend=self,
                                                token=token),
                    html_body=render_template('relationship/email/friend_request.html',
                                                user=friend, friend=self,
                                                token=token))
        except:
            request.delete()

        return None

    def get_requested_friends(self):
        """Return list of persons with unconfirmed friend requests."""
        requested = []
        for request in self.sentfriendrequests:
            if request.requested_friend not in requested:
                requested.append(request.requested_friend)
        return requested

    def get_friend_approval_choices(self):
        if len(self.receivedfriendrequests) > 0:
            choices = [(request.id, request.requestor.full_name) for request in
                       self.receivedfriendrequests]
        else:
            choices = None
        return choices

    def get_received_friend_requests(self):
        """Get list of persons that sent user unconfirmed friend requests.
           Returns None if no requests."""
        if len(self.receivedfriendrequests) > 0:
            requested = []
            for request in self.receivedfriendrequests:
                if request.requestor not in requested:
                    requested.append(request.requestor)
            return requested
        else:
            return None

    @staticmethod
    def verify_friend_request_token(token):
        """Check friend request token and returns request if valid and error
           if invalid."""
        try:
            request_id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['request']
            request = FriendRequest.query.get(request_id)
        except:
            request = None
        return request

    def get_group_list(self):
        """Generate list of tuples containing group's id and name."""
        group_list = []
        for group in self.groups:
            group_list.append((group.id, group.name))
        return group_list

    def get_group_admin_choices(self):
        """Get group admin approval choices for approval form.
        Outputs list of tuples containing request id and
        group name / requestor name."""
        choices = []
        for group in self.group_admin:
            for request in group.join_requests:
                choice = (request.id, f"{request.group.name} - {request.requestor.full_name}")
                choices.append(choice)
        return choices

    def get_group_approval_requests(self):
        """Return pending approval requests for groups user is admin for."""
        pending = []
        # iterate through groups that user is admin
        for group in self.group_admin:
        # for each group, iterate through received requests & add to list
            for request in group.join_requests:
                pending.append(request)
        if pending == []:
            return None
        else:
            return pending

    def get_group_request_token(self, request):
        """Get group request token.
        Inputs:
        request: GroupRequest to join the group.
        """

        payload = {"request": request.id}
        expiration = None
        return self._get_token(payload, expiration)

    def send_group_request(self, group):
        """Send group admin request to join & update GroupRequest table."""
        # create group join request
        request = GroupRequest(group_id=group.id,
                                requestor_id=self.id,
                                date_sent=date.today())
        request.save()
        try: 
            token = self.get_group_request_token(request)
            send_email('Ask a Neighbor: Group Join Request',
                    sender=current_app.config['ADMINS'][0],
                    recipients=[group.admin.email],
                    text_body=render_template('relationship/email/group_request.txt',
                                                user=group.admin, group=group,
                                                new_member=self, token=token),
                    html_body=render_template('relationship/email/group_request.html',
                                                user=group.admin, group=group,
                                                new_member=self, token=token))
        except:
            # delete request if request fails to send.
            request.delete()
            raise

        return None

    @staticmethod
    def verify_group_request_token(token):
        """Check group request token and returns GroupRequest if valid and error
           if invalid."""
        try:
            request_id = jwt.decode(token, current_app.config['SECRET_KEY'],
                                    algorithms=['HS256'])['request']
            request = GroupRequest.query.get(request_id)

        except:
            request = None
        return request

    def _addfriend(self, person):
        """Add friend relationship bi-directionally."""
        self.friends.append(person)
        person.friends.append(self)

    def _addgroup(self, group):
        """Add group relationship."""
        self.groups.append(group)

    def add(self, relation, request=None):
        """Determine whether to add group or friend and call approp method."""
        if type(relation) == User:
            self._addfriend(relation)
        elif type(relation) == Group:
            self._addgroup(relation)
        if request:
            request.delete()
        self.save()

    def _removefriend(self, person):
        self.friends.remove(person)
        person.friends.remove(self)

    def _removegroup(self, group):
        self.groups.remove(group)

    def remove(self, relation):
        if type(relation) == User:
            self._removefriend(relation)
        elif type(relation) == Group:
            self._removegroup(relation)


    def summary(self):
        """Return user object with review summary information(avg/count)"""
        # need to accomodate zero reviews...joins makes it unable to calc
        summary = (db.session.query(func.avg(Review.rating).label("average"),
                                    func.avg(Review.cost).label("cost"),
                                    func.count(Review.id).label("count"))
                             .filter(User.id == self.id)
                             .join(User)
                             .first())
        return summary

    def profile_reviews(self):
        """Returns review object query."""
        reviews = (db.session.query(Review).join(User)
                                           .filter(User.id == self.id))
        return reviews

    def search_providers(self, form):
        """Returns filtered provider query object."""
        category = Category.query.filter_by(id=form.category.data).first()
        # common joins and filters used by all queries
        filter_args = [Provider.categories.contains(category),
                       Address.city.ilike(form.city.data),
                       Address.state_id == form.state.data]
        join_args = [Provider.address, Provider.reviews, Review.user]
        # update filter for relationship filters
        if form.friends_only.data is True:
            filter_args.append(User.friends.contains(self))
        elif form.groups_only.data is True:
            groups = [g.id for g in self.groups]
            filter_args.extend([Group.id.in_(groups), User.id != self.id])
            join_args.extend([User.groups])

        providers = (db.session.query(Provider,
                                      func.avg(Review.rating).label("average"),
                                      func.avg(Review.cost).label("cost"),
                                      func.count(Review.id).label("count"))
                               .join(*join_args)
                               .filter(*filter_args)
                               .group_by(Provider.name)
                               .order_by(Provider.name))
        return providers

    def __repr__(self):
        return f"<User {self.username}>"


class FriendRequest(Model):
    """Tracks pending friend requests not yet verified."""

    __tablename__ = "friendrequest"

    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                     ondelete="CASCADE"),
                          nullable=False)
    requestor_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                       ondelete="CASCADE"), 
                             nullable=False)
    date_sent = db.Column(db.Date, index=True, nullable=False)

    def __repr__(self):
        return f"<FriendRequest {self.requestor.full_name} {self.requested_friend.full_name}>"

class GroupRequest(Model):
    """Tracks pending group requests not yet verified."""

    __tablename__ = "grouprequest"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id",
                                                    ondelete="CASCADE"),
                         nullable=False)
    requestor_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                        ondelete="CASCADE"),
                             nullable=False)
    date_sent = db.Column(db.Date, index=True, nullable=False)

    def __repr__(self):
        return f"<FriendRequest {self.requestor.full_name} {self.requested_group.name}>"

class Category(Model):
    """List service categories.
    Relationships:
        Parent of: Review
        Many to Many: Provider
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    providers = db.relationship("Provider", secondary=category_provider_table,
                                backref="categories")
    reviews = db.relationship("Review", backref="category")

    @staticmethod
    def category_list():
        """Query db to populate state list on forms."""
        if current_app.config['TESTING'] == True:
            list = current_app.config['TEST_CATEGORIES']
        else:
            try:
                list = [(c.id, c.name) for c in Category.query.order_by("name")]
            except OperationalError:
                list = [(1, "Test")]
        return list

    def __repr__(self):
        return f"<Category {self.name}>"


class Provider(Model):
    """Create service provider record.
    Relationship:
        Parent of: review
        Child of: address
        Many to Many: category
    """
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    _telephone = db.Column(db.String(24), unique=True, nullable=False)

    address = db.relationship("Address", backref="provider", uselist=False,
                              passive_deletes=True)
    reviews = db.relationship("Review", backref="provider")

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name is not None:
            name = capwords(name)
        self._name = name

    @hybrid_property
    def telephone(self):
        return self._telephone

    @telephone.setter
    def telephone(self, telephone):
        if telephone is not None:
            telephone = re.sub('\D+', '', telephone)
        self._telephone = telephone

    def profile(self, filter):
        """Return tuple of provider object with review summary information(avg/count)
        form: boolean form with friend/group filters
        """
        # base filter and join args
        filter_args = [Provider.id == self.id]
        join_args = [Review.provider, Review.user]
        # update filter and joins for relationship filters
        if filter['friends_only'] is True:
            filter_args.append(User.friends.contains(current_user))
        elif filter['groups_only'] is True:
            groups = [g.id for g in current_user.groups]
            join_args.extend([User.groups])
            filter_args.extend([Group.id.in_(groups), User.id != current_user.id])
        summary = (db.session.query(func.avg(Review.rating).label("average"),
                                    func.avg(Review.cost).label("cost"),
                                    func.count(Review.id).label("count"))
                             .join(*join_args)
                             .filter(*filter_args)
                             .first())
        return (self, summary.average, summary.cost, summary.count)

    def profile_reviews(self, filter):
        """Returns review object query."""
        # base filter and join args
        filter_args = [Provider.id == self.id]
        join_args = [Review.provider, Review.user]

        # update filter and joins for relationship filters
        if filter['friends_only'] is True:
            filter_args.append(User.friends.contains(current_user))
        elif filter['groups_only'] is True:
            groups = [g.id for g in current_user.groups]
            join_args.extend([User.groups])
            filter_args.extend([Group.id.in_(groups), User.id != current_user.id])
        reviews = (db.session.query(Review).join(*join_args)
                                           .filter(*filter_args))
        return reviews

    def __repr__(self):
        return f"<Provider {self.name}>"


class Review(Model):
    """Class to create define review table in db.
    Relationships:
        Parent of: Picture
        Child of: Category, User, Provider
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id"),
                            nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"),
                            nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    _description = db.Column(db.String(120))
    service_date = db.Column(db.Date)
    _comments = db.Column(db.Text)

    pictures = db.relationship("Picture", backref="review",
                               passive_deletes=True)

    @hybrid_property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if description == "" or description is None:
            self._description = None
        else:
            self._description = description.capitalize()

    @hybrid_property
    def comments(self):
        return self._comments

    @comments.setter
    def comments(self, comments):
        if comments == "" or comments is None:
            self._comments = None
        else:
            self._comments = comments.capitalize()

    def _repr__(self):
        return f"<Rating {self.provider}, {self.rating}>"


class Picture(Model):
    """Class to define picture table in db, to be linked with reviews.
    picture_path - location of picture in file storage system
    Relationships:
        Child of: Review
    """
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    thumb = db.Column(db.String(120), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("review.id",
                                                    ondelete="CASCADE"),
                          nullable=False)
    def __repr__(self):
        return f"<Picture {self.name}>"

class Group(Model):
    """Groups that users can belong to.
    Relationships:
        Many to Many: User
        One to one: User/admin
    """
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    _description = db.Column(db.String(120), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    members = db.relationship("User", secondary=user_group,
                              backref="groups")
    admin = db.relationship("User", backref="group_admin")
    join_requests = db.relationship("GroupRequest", backref="group")

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = capwords(name)

    @hybrid_property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if description == "" or description is None:
            self._description = None
        else:
            self._description = description.capitalize()

    def __repr__(self):
        return f"<Group {self._name}>"
