from collections import namedtuple
import copy
from datetime import datetime, date
from operator import attrgetter
import re
from string import capwords

from flask import current_app, render_template, session
from flask_login import UserMixin, current_user
import jwt
from sqlalchemy import CheckConstraint, func as saFunc, or_, and_, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, validates
from sqlalchemy.sql import exists, func
from sqlalchemy.sql.expression import desc
from threading import Thread
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import Model
from app.extensions import db
from app.utilities.email import decode_token, get_token, send_email
from app.utilities.geo import getDistance, geocode, AddressError, APIAuthorizationError
from app.utilities.helpers import noneIfEmptyString

addressTuple = namedtuple('addressTuple', ['line1', 'city', 'state', 'zip'])

class dbQuery(object):
    """Helper class to to simplify SQLalchemy orm queries.
    
    Attributes:
        query_args (list): fields that are returned
        select_from (class): class that is right side of query
        join_args (list): fields at which joins take place on query
        outerjoin_args (list): left outerjoin field arguments.
        filter_args (list): filters to be applied.  
        group_by (list): fields used to group return values
        sort_args (list): fields used to determine sort order
        limit (integer): defaults to none, limits number of query results
    
    Methods:
        getQuery: returns SQL query.  Not yet submitted to db.
        all: calls getQuery and submits to db, returning all results
        copy: creates copy of existing query
    
    """
    def __init__(self, limit=None):
        self.query_args = []
        self.select_from = None
        self.join_args = []
        self.outerjoin_args = []
        self.filter_args = []
        self.group_by = []
        self.sort_args = []
        self.limit = limit
    
    def getQuery(self):
        """returns SQL query.  Not yet submitted to db."""
        return db.session.query(*self.query_args)\
                                .select_from(self.select_from)\
                                .join(*self.join_args)\
                                .outerjoin(*self.outerjoin_args)\
                                .filter(*self.filter_args)\
                                .group_by(*self.group_by)\
                                .order_by(*self.sort_args)\
                                .limit(self.limit)

    def all(self):
        """Creates sql query and submits to db, returning list of results."""
        return self.getQuery().all()

    def copy(self):
        """Copies existing query, returning new query."""
        new = copy.copy(self)
        for field in self.__dict__.keys():
            setattr(new, field, copy.copy(getattr(self, field)))
        return new

    def __iter__(self):
        return dbQueryIterator(self)


class dbQueryIterator(object):
    def __init__(self, source):
        self.source = source
        self.fields = list(source.__dict__.keys())
    
    def __next__(self):
        if len(self.fields) > 0:
            return getattr(self.source, self.fields.pop(0))
        else:
            raise StopIteration

# many to many table linking users with groups
user_group = db.Table('user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))


# many to many table linking providers to multiple categories
category_provider = db.Table('category_provider', db.Model.metadata,
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
    def list():
        """Query db to populate state list on forms."""
        if current_app:
            if current_app.config['TESTING'] == True:
                list = current_app.config['TEST_STATES']
            else:
                list = [(s.id, s.name) for s in State.query.order_by("name")]
        else:
            list = [(None, None)]
        return list

    def __repr__(self):
        return f"<State {self.name}>"


class Address(Model):
    """Addresses used for users and providers.

    Args:
        id (int): id set by db
        unknown (bool): for businesses, if person entering business doesn't know
                       full address, allows user to only enter city/state. Must
                       be added prior to other lines
        line1 (str): hybrid property, 1st address line
        line2 (str): hybrid property, 2nd address line
        zip (str): zip code
        city (str): hybrid property, city name
        user_id (int): foreign key, user_id if user associated with address
        provider_id (int): foreign key, provider id if business assoc with
                           address
        state_id (int): foreign key, id of address's state
        latitude (flt): latitude of address coordinates
        longitude (flt): longitude of address coordinates
    
    Methods:
        update: overrides superclass update method.  calls get_coordinates if
                address changed
        get_coordinates: retrieves updated coordinates based on address and
                         updates latitude and longitude
        
    Relationships:
        Parent of:
        Child of: State, User, Provider
    """
    id = db.Column(db.Integer, primary_key=True)
    unknown = db.Column(db.Boolean, default=False, index=True)
    _line1 = db.Column(db.String(128))
    _line2 = db.Column(db.String(128))
    zip = db.Column(db.String(20), index=True)
    _city = db.Column(db.String(64), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                  ondelete="CASCADE"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id",
                                                      ondelete="CASCADE"))
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), nullable=False)
    latitude = db.Column(db.Float(precision='8,6'), index=True)
    longitude = db.Column(db.Float(precision='9,6'), index=True)


    def __init__(self, **kwargs):
        super(Address, self).__init__(**kwargs)
        self.coordinates = self._initializeCoordinates

    def update(self, commit=True, **kwargs):
        """Update address and coordinates and saves changes to db."""
        changed = False
        for attr, value in kwargs.items():
            if value != getattr(self, attr):
                setattr(self, attr, value)
                if attr not in ['latitude', 'longitude']:
                    changed = True
        if changed is True:
            self.get_coordinates()
        return commit and self.save() or self

    @hybrid_property
    def line1(self):
        return self._line1

    @line1.setter
    def line1(self, line1):
        """Title cases line1 when it is being set."""
        if line1 is not None:
            line1 = line1.title()
        self._line1 = line1

    @validates('_line1', 'zip')
    def validate_line1zip(self, key, field):
        if isinstance(self.unknown, bool):
            assert field is not None or self.unknown is True
        return field
       

    @hybrid_property
    def line2(self):
        return self._line2

    @line2.setter
    def line2(self, line2):
        """Title cases line2 when it is being set."""
        if line2 is not None:
            line2 = line2.title()
        self._line2 = line2


    @hybrid_property
    def city(self):
        return self._city

    @city.setter
    def city(self, city):
        """Title cases city when it is being set."""
        if city is not None:
            city = city.title()
        self._city = city

    
    @hybrid_property
    def coordinates(self):
        """Returns tuple of latitude and longitude."""
        if self.latitude == None or self.longitude == None:
            return None
        else:
            return (self.latitude, self.longitude)

    @coordinates.setter
    def coordinates(self, coordinateFunc):
        """Sets lat/long based on function passed in."""
        coordinateFunc()

    def _initializeCoordinates(self):
        """Gets coordinates at initialization unless included with constructor."""
        if self.longitude is None or self.latitude is None:
            self.get_coordinates()

    def get_coordinates(self):
        """Get latitude and longitude for given address and store in db.
        
        Raises:
            AddressError: if geocode determines invalid address submitted.
        
        """
        if self.state_id is not None:
            state = State.query.get(self.state_id).state_short
        else:
            state = ""
        address = f"{self.line1}, {self.city}, {state} {self.zip}"
        try:
            self.latitude, self.longitude = geocode(address)[0]
        except (AddressError, APIAuthorizationError):
            raise
        return None
    
    @property
    def distance(self):
        """Return geodesic distance from location stored in session to address."""
        origin = session['location']['coordinates']
        distance = getDistance(origin, self.coordinates)
        return distance


    def __repr__(self):
        return f"<Address {self.line1}, {self.city}, {self.state}>"


class User(UserMixin, Model):
    """Creates user class.

    Attributes:
        id (int): db id for user, automatically created by db
        username (str): unique username created by user to login. name visible
            to users they are not related to
        email (str): hybrid-property, email address of user, unique
        email_verified (bool): true once user has verified their email address
            via receipt of email
        password_hash (str): hashed password stored in database
        password_set_date (Date): date password was last reset
        first_name (str): hybrid property, first name of user
        last_name (str): hybrid property, last name of user
        full_name (str): property, concatenation of first and last name
        address (Address): Address object of user
        reviews (list): list of Reviews created by user
        friends (list): list of Users that user is friends with
        sentfriendrequests (list): list of unconfirmed friend requests sent
        receivedfriendrequests (list): lists of unconfirmed friend requests
            received by user
        sentgrouprequests (list): lists of unconfirmed requests to join a group

    Methods:
        set_password: Store submitted password as hash.
        check_password: Compares hashed submitted password to store password hash.
        send_password_reset_email: send email for user to reset password.
        verify_password_reset_token: verify email link token is valid to allow 
        password reset.
        send_email_verification_email: send email to verify email address.
        verify_email_verification_token: verify email verification weblink.
        add: add group or friend to user
        remove: remove group or friend
        summary: returns summary info on user's reviews (rating, cost, count)
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    _email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(128))
    password_set_date = db.Column(db.Date, index=True)
    _first_name = db.Column(db.String(64), index=True, nullable=False)
    _last_name = db.Column(db.String(64), index=True, nullable=False)

    address = db.relationship("Address", backref="user", 
                              cascade="all, delete-orphan", lazy=False,
                              uselist=False, passive_deletes=True)
    reviews = db.relationship("Review", backref="user",
                              cascade="all, delete-orphan",
                              passive_deletes=True)
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
    _email_token_key = 'verify_email'
    _password_token_key = 'reset_password'

    @hybrid_property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        """Title cases first name."""
        if first_name is not None:
            first_name = first_name.title()
        self._first_name = first_name

    @hybrid_property
    def last_name(self):
        return self._last_name


    @last_name.setter
    def last_name(self, last_name):
        """Title cases last name when being set."""
        if last_name is not None:
            last_name = last_name.title()
        self._last_name = last_name

    @hybrid_property
    def full_name(self):
        """Returns concatenation of first and last name."""
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        """"Only sets email if change from current.
        
        Saves new email only if changing from what is stored in db.  Avoids
        unique constraint in db.
        """
        if email != self._email:
            self._email = email
        else:
            pass
    
    @validates('address', include_removes=True)
    def validate_address(self, key, address, is_remove):
        if is_remove:
            raise ValueError("Address for user is required.")
        else:
            assert address is not None
        return address


    def set_password(self, password):
        """Converts plaintext password to hash and stores in db."""
        self.password_hash = generate_password_hash(password)
        self.password_set_date = date.today()
        self.save()

    def check_password(self, password):
        """Checks plaintext password entered by user vs hash in db."""
        return check_password_hash(self.password_hash, password)

    def _get_reset_password_token(self, expiration=10):
        """Get password reset token."""
        payload = {self._password_token_key: self.id}
        expiration = 10  # 10 minutes
        return get_token(payload, expiration)

    def send_password_reset_email(self):
        """Send email to allow user to reset password."""
        token = self._get_reset_password_token()
        send_email('Ask Your Peeps: Password Reset',
                sender=current_app.config['ADMINS'][0],
                recipients=[self.email],
                cc = None,
                text_body=render_template('auth/email/reset_password_msg.txt',
                                            user=self, token=token),
                html_body=render_template('auth/email/reset_password_msg.html',
                                            user=self, token=token))

    @staticmethod
    def verify_password_reset_token(token):
        """Static method to verify password reset token.

        Args:
            token (Str): token sent by user when clicking on password reset link

        Returns: 
            User:  User corresponding to id in token
            None:  if token doesn't validate
        """

        try:
            id = decode_token(token, User._password_token_key)
        except:
            return
        return User.query.get(id)

    def _get_email_verification_token(self, expiration=10*60*24):
        """Get jwt token for email address verification."""
        payload = {self._email_token_key: self.id}
        expiration = expiration # 10 days
        return get_token(payload, expiration)

    def send_email_verification(self):
        """Send email to request email verification."""
        token = self._get_email_verification_token()
        send_email('Ask Your Peeps: Email Verification',
                   sender=current_app.config['ADMINS'][0],
                   recipients=[self.email],
                   cc = None,
                   text_body=render_template('auth/email/verify_email_msg.txt',
                                             user=self, token=token),
                   html_body=render_template('auth/email/verify_email_msg.html',
                                             user=self, token=token))

    @staticmethod
    def verify_email_verification_token(token):
        """Static method to check email verification token.
        
        Args:
           token (str): token from email user receives to verify email
        Returns:
            user (User or None): user if token verifies, else None
            error (str): error type (expired or invalid) if token doesn't verify
        """

        try:
            id = decode_token(token, User._email_token_key)
            user = User.query.get(id)
            error = None
        except jwt.ExpiredSignatureError:
            error = "Expired"
            user = None
        except:
            error = "Invalid"
            user = None
        return (user, error)

    def _addfriend(self, person):
        """Add friend relationship bi-directionally."""
        self.friends.append(person)
        person.friends.append(self)

    def _addgroup(self, group):
        """Add group relationship."""
        self.groups.append(group)

    def add(self, relation, request=None):
        """Determine whether to add group or friend and call approp method.
        
        Args:
            relation (object): group or user being added as group or friend.
            request (friendrequest or grouprequest): request to be deleted after
                relation added
        Returns:
            None
        
        """
        if type(relation) == User:
            self._addfriend(relation)
        elif type(relation) == Group:
            self._addgroup(relation)
        if request:
            request.delete()
        self.save()

    def _removefriend(self, person):
        if person not in self.friends:
            raise ValueError("Can't unfriend person user isn't friends with")
        else:
            self.friends.remove(person)
            person.friends.remove(self)

    def _removegroup(self, group):
        if group not in self.groups:
            raise ValueError("Can't remove group user is not member of.")
        else:
            self.groups.remove(group)

    def remove(self, relation):
        """Removes relation (group or friend) from approp relation list.
        
        Args:
            relation (object): group or user being removed.

        Returns:
            None
        """
        try:
            if type(relation) == User:
                self._removefriend(relation)
            elif type(relation) == Group:
                self._removegroup(relation)
        except ValueError:
            db.session.rollback()
            raise

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

    def __repr__(self):
        return f"<User {self.username}>"


class FriendRequest(Model):
    """Request for 1 user to become friends with another user.

    Attributes:
        id (int): id for specific request
        friend_id (int): id for person requesting user wants to be friends with
        requestor_id (int): user id for person initiating request
        date_sent (date): date request is sent
        token_key (str): key used to generate request token
        requestor (User): User initiating request
        requested_friend (User): User receiving friend request

    Methods:
        send: send friend request email from requestor to friend
        verify_token: verifies token in request email link
    
    """

    __tablename__ = "friendrequest"

    id = db.Column(db.Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                     ondelete="CASCADE"),
                          nullable=False)
    requestor_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                       ondelete="CASCADE"), 
                             nullable=False)
    date_sent = db.Column(db.Date, index=True, nullable=True)
    token_key = 'request'


    def __repr__(self):
        return f"<FriendRequest {self.requestor.full_name} {self.requested_friend.full_name}>"

    def _get_request_token(self):
        """Get friend request token."""
        payload = {self.token_key: self.id}
        expiration = None
        return get_token(payload, expiration)

    def send(self):
        """Send friend request to requested friend
        Args:
            None
        Returns:
            None
        """

        token = self._get_request_token()
        send_email('Ask Your Peeps: Friend Verification',
                sender=current_app.config['ADMINS'][0],
                recipients=[self.requested_friend.email],
                cc=None,
                text_body=render_template('relationship/email/friend_request.txt',
                                            user=self.requested_friend,
                                            friend=self.requestor,
                                            token=token),
                html_body=render_template('relationship/email/friend_request.html',
                                            user=self.requested_friend,
                                            friend=self.requestor,
                                            token=token))
        self.date_sent = date.today()
        return None

    @staticmethod
    def verify_token(token):
        """Verifies friend request token is valid.
        
        Check friend request jwt token, returns request object if valid and None
           if invalid.
        Args:
            token (str): token returned by friend when approving request
        
        Returns:
            request (FriendRequest) if valid or None if invalid
        """

        try:
            request_id = decode_token(token, FriendRequest.token_key)
            request = FriendRequest.query.get(request_id)
        except:
            request = None
        return request

class GroupRequest(Model):
    """Request for user to join a group.
    
    Attributes:
        id (int): id for specific request
        group_id (int): id of group user would like to join
        requestor_id (int): user id for person initiating request
        date_sent (date): date request is sent
        token_key (str): key used to generate request token
        requestor (User): User initiating request
        group (Group): Group requestor is asking to join

    Methods:
        send: send group request email from requestor to group_admin
        verify_token: verifies token in request email link
        get_pending: returns list of pending approval request for group admin
    
    """

    __tablename__ = "grouprequest"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id",
                                                    ondelete="CASCADE"),
                         nullable=False)
    requestor_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                        ondelete="CASCADE"),
                             nullable=False)
    date_sent = db.Column(db.Date, index=True, nullable=True)
    token_key = 'request'

    def _get_request_token(self):
        """Get group request token."""
        payload = {self.token_key: self.id}
        expiration = None
        return get_token(payload, expiration)

    def send(self):
        """Send group join request to group admin and cc's requesting user
        Args:
            None
        Returns:
            None
        """
        # create group join request
        token = self._get_request_token()
        send_email('Ask Your Peeps: Group Join Request',
                sender=current_app.config['ADMINS'][0],
                recipients=[self.group.admin.email],
                cc = None,
                text_body=render_template('relationship/email/group_request.txt',
                                            user=self.group.admin, group=self.group,
                                            new_member=self.requestor, token=token),
                html_body=render_template('relationship/email/group_request.html',
                                            user=self.group.admin, group=self.group,
                                            new_member=self.requestor, token=token))
        self.date_sent = date.today()
        return None

    @staticmethod
    def verify_token(token):
        """Verifies group request email token.
        
        Check group request token and returns GroupRequest if valid and None
           if invalid.
        Args:
           token (str): token return by group admin upon approving request email
        Returns:
            request (GroupRequest) if valid or None
        """
        try:
            request_id = decode_token(token, GroupRequest.token_key)
            request = GroupRequest.query.get(request_id)
        except:
            request = None
        return request



    def __repr__(self):
        return f"<GroupRequest {self.requestor.full_name} {self.group.name}>"

    @staticmethod
    def get_pending(user):
        """Static mehtod, Return pending approval requests user is admin for.
        
        Args:
            user (User): user object of group_admin
        Returns:
            list of GroupRequests
        """
        pending = GroupRequest.query.join(Group)\
                                    .filter(Group.admin_id == user.id).all()
        return pending
 
class Sector(Model):
    """Business sector that categories are a member of.

    Attributes:
        id (int): id of sector, primary key for db table
        name (str): name of sector
        categories (list): list of categories in sector
    
    Methods:
        list: Generates a list of tuples of sector id and name

    Relationships:
        Parent of: category
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)

    categories = db.relationship("Category", backref=backref("sector",
                                                             uselist=False))

    @staticmethod
    def list():
        """Generate list of tuples of sector id/name
        
        Args:
            None
        Returns:
            List of tuples (id, name)
        """        
        
        if current_app:
            if current_app.config['TESTING'] is True:
                list = current_app.config['TEST_SECTOR']
            else:
                list = [(s.id, s.name) for s in Sector.query.order_by("name")]
        else:
            list = []
        return list

    def __repr__(self):
        return f"<Sector {self.name}>"


class Category(Model):
    """Business categories which businesses fall into
    
    Attributes:
        id (int): id of category, primary key for db
        name (str): name of category, must be unique
        sector_id (id): foreign key, id for sector into which category falls
        providers (list): list of providers in the category
        reviews (list): list of reviews in the category
    
    Methods:
        list: generate list of tuples with category id/name

    Relationships:
        Parent of: Review
        Many to Many: Provider
        Child of: Sector
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"), nullable=False)
    # service_area_required = db.Column(db.Boolean, default=False)

    providers = db.relationship("Provider", secondary=category_provider,
                                backref="categories")
    reviews = db.relationship("Review", backref="category")

    @staticmethod
    def list(sector_id):
        """Generate list of tuples of category id and name for given sector
        
        Args:
            sector_id (int): sector id to use as look up for categories
        Returns:
            List of tuples (id, name)
        
        """

        if current_app:
            if sector_id is not None:
                sector = Sector.query.get(sector_id)
                catList = (Category.query.filter(Category.sector == sector)
                                            .order_by(Category.name)).all()
            else:
                catList = Category.query.all()
            catList = [(category.id, category.name) for category in catList]                
        else:
            catList = []
        return catList

    def __repr__(self):
        return f"<Category {self.name}>"


class Provider(Model):
    """Container for business/provider information.

    Attributes:
        id (int): db primary key for record
        name (str): hybrid property, name of business
        email (str): optional, email address of business.  must be unique
        telephone (str): 10 digit telephone number, must be unique
        address (Address): address of business
        reviews (List): list of Reviews for the business
        categories (list): list of categories that business serves

    Relationship:
        Parent of: review
        Child of: address
        Many to Many: category
    
    Methods:
        list: generate list of provider id and name based on category.
        search: generate list of providers based on search and social filters
        profile: return tuple of provider summary statistics / provider object
            based on social filter
    
    """
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    _telephone = db.Column(db.String(24), unique=True, nullable=False)

    address = db.relationship("Address", backref="provider", uselist=False,
                              passive_deletes=True,
                              cascade="all, delete-orphan")
    reviews = db.relationship("Review", cascade="all, delete-orphan", 
                              backref="provider", passive_deletes=True)

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name is not None:
            name = name
        self._name = name

    @hybrid_property
    def telephone(self):
        return self._telephone

    @telephone.setter
    def telephone(self, telephone):
        if telephone is not None:
            telephone = re.sub('\D+', '', telephone)
        self._telephone = telephone

    @validates('address', include_removes=True)
    def validate_address(self, key, address, is_remove):
        if is_remove:
            raise ValueError("Address for provider is required.")
        else:
            assert address is not None
        return address
    
    @hybrid_property
    def categoryList(self):
        return self._categoryList    
    
    @hybrid_property
    def review_count(self):
        return len(self.reviews)
    
    @hybrid_property
    def average_rating(self):
        try:
            total = sum([review.rating for review in self.reviews])
            return total/self.review_count
        except ZeroDivisionError:
            return 0
    
    @hybrid_property
    def average_cost(self):
        try:
            total = sum([review.cost for review in self.reviews])
            return total/self.review_count
        except ZeroDivisionError:
            return 0  

    @staticmethod
    def list(category_id, format='tuple'):
        """Returns list of provider id and name based on category filter
        
        Args:
            category_id (int): category id to filter providers by
            format (str): output format (dict or tuple) for id/name output in
                          list

        Returns:
            list: list of providers (id and name)
        
        Raises:
            ValueError: if format other than dict or tuple is passed as
                        parameter
        """

        category = Category.query.get(category_id)
        query = (Provider.query.filter(Provider.categories.contains(category))
                               .order_by(Provider.name)).all()
        if format == 'dict':
            provider_list = [{"id": provider.id, "name": provider.name} for provider
                            in query]
        elif format == 'tuple':
            provider_list = [(provider.id, provider.name) for provider
                            in query]
        else:
            raise ValueError("incorrect format")   
        return provider_list


    @classmethod
    def search(cls, filters, sort=None, limit=None):
        """Search for providers meeting specified filters and social filters.

        Search for providers based on category and distance from search origin.
        Sorting by name or average rating are done by database.  Distance sort
        done outside of this method.  
        
        Args:
            filters (dict): search filters (category, name, location, id, etc)
            sort (str): sort criteria to use.  name, distance, rating
            limit (int): optional, defaults to none, limits number of results 
                         returned
        Returns:
            list: list of providers plus summary statistics for each provider,
                  sorted by provider name
        """

        q = dbQuery()
        q.select_from = Provider
        q.limit = limit
        q.group_by = [Provider.id, Provider.name, Provider.email,
                      Provider.telephone, Address.line1, Address.line2,
                      Address.city, State.state_short, Address.zip,
                      Address.latitude, Address.longitude]
        q.join_args = [Provider.address, Address.state, Provider.categories]
        q.outerjoin_args = [Provider.reviews, Review.user]
        q.query_args = [Provider.id.label('id'), Provider.name.label('name'),
                        Provider.email.label('email'), 
                        Provider.telephone.label('telephone'),
                        Address.line1.label('line1'),
                        Address.line2.label('line2'),
                        Address.city.label('city'),
                        State.state_short.label('state_short'),
                        Address.zip.label('zip'),
                        Address.latitude.label('latitude'),
                        Address.longitude.label('longitude'),
                        saFunc.group_concat(Category.name.distinct()).label("categories"),
                        func.avg(Review.rating).label('reviewAverage'),
                        func.avg(Review.cost).label('reviewCost'),
                        func.count(Review.id.distinct()).label('reviewCount'),
                        saFunc.group_concat(Review.id).label('reviewIDs')
                      ]

        if sort and sort == "rating":
            q.sort_args = [desc("reviewAverage"), Provider.name]
        else:
            q.sort_args = [Provider.name]

        if "category" in filters.keys():
            q.filter_args.append(Provider.categories.contains(filters['category']))
            # q.filter_args.append(Category.id == filters['category'].id)

        if "location" in filters.keys():
            q.filter_args.extend([Address.longitude > filters['location'].minLong,
                               Address.longitude < filters['location'].maxLong,
                               Address.latitude > filters['location'].minLat,
                               Address.latitude < filters['location'].maxLat])

        if "id" in filters.keys():
            q.filter_args.append(Provider.id == filters['id'])

        if "name" in filters.keys() and filters['name'] not in ["", None]:
            name = f"%{filters['name']}%"
            q.filter_args.append(Provider.name.ilike(name))

        reviewed = True in [filters.get('friends'), filters.get('groups'),
                            filters.get('reviewed')]
        if reviewed:
            q.outerjoin_args = []
            q.join_args.extend([Provider.reviews, Review.user])
            friendsFilter = User.friends.contains(current_user)
            groups = [g.id for g in current_user.groups]
            groupsFilter = (and_(Group.id.in_(groups), User.id != current_user.id))
            if filters.get('friends') is True and filters.get('groups') is False:
                q.filter_args.append(friendsFilter)
                providers = q.getQuery()
            elif filters.get('groups') is True and filters.get('friends') is False:
                q.filter_args.append(groupsFilter)
                q.join_args.append(User.groups)
                providers = q.getQuery()

            elif filters.get('groups') is True and filters.get('friends') is True:
                sort_args = q.sort_args[:]
                q.sort_args.clear()
                q.group_by.insert(0, 'reviewID')
                q.group_by.extend(['rating', 'cost'])
                q.query_args[-4:] = []
                q.query_args.extend([Review.id.label('reviewID'),
                                      Review.rating.label('rating'),
                                      Review.cost.label('cost')])
                qF = q.copy()
                qG = q.copy()
                qF.filter_args.append(friendsFilter)

                qG.filter_args.append(groupsFilter)
                qG.join_args.append(User.groups)

                sub = qF.getQuery().union(qG.getQuery()).subquery(name='sub')
                qP = dbQuery()
                qP.select_from = sub
                qP.query_args = [sub.c.id, sub.c.name, sub.c.email, 
                        sub.c.telephone, sub.c.line1, sub.c.line2, sub.c.city,
                        sub.c.state_short, sub.c.zip, sub.c.latitude,
                        sub.c.longitude, sub.c.categories,
                        func.avg(sub.c.rating).label('reviewAverage'),
                        func.avg(sub.c.cost).label('reviewCost'),
                        func.count(sub.c.reviewID).label('reviewCount'),
                        saFunc.group_concat(sub.c.reviewID).label('reviewIDs')
                ]
                qP.group_by = qP.query_args.copy()[:-4]    

                if sort and sort == "rating":
                    qP.sort_args = [desc("reviewAverage"), sub.c.name]
                else:
                    qP.sort_args = [sub.c.name]

                q = qP

        providers = q.getQuery()
        providers=providers.all()
        return providers


    def profile(self, filter):
        """Return tuple of provider object with review summary information(avg/count)
        form: boolean form with friend/group filters
        """
        # base filter and join args
        q = dbQuery()
        q.select_from = Review
        q.filter_args = [Provider.id == self.id]
        q.join_args = [Review.provider, Review.user]
        q.query_args = [func.avg(Review.rating).label("average"),
                        func.avg(Review.cost).label("cost"),
                        func.count(Review.id).label("count")]
        friendsFilter = User.friends.contains(current_user)
        groups = [g.id for g in current_user.groups]
        groupsFilter = (and_(Group.id.in_(groups), User.id != current_user.id))                        
        # update filter and joins for relationship filters
        if filter['friends_filter'] is True and filter['groups_filter'] is False:
            q.filter_args.append(friendsFilter)
        if filter['groups_filter'] is True and filter['friends_filter'] is False:
            q.join_args.append(User.groups)
            q.filter_args.append(groupsFilter)
        if filter['groups_filter'] is True and filter['friends_filter'] is True:
            q.query_args = [Review.id.label('reviewID'),
                                    Review.rating.label('rating'),
                                    Review.cost.label('cost')]           
            qF = q.copy()
            qG = q.copy()
            qF.filter_args.append(friendsFilter)

            qG.filter_args.append(groupsFilter)
            qG.join_args.append(User.groups)

            sub = qF.getQuery().union(qG.getQuery()).subquery(name='sub')

            q = dbQuery()
            q.select_from = sub
            q.query_args = [func.avg(sub.c.rating).label("average"),
                            func.avg(sub.c.cost).label("cost"),
                            func.count(sub.c.reviewID).label("count")]            

        summary = q.getQuery().first()
        return (self, summary.average, summary.cost, summary.count)
    
    def __repr__(self):
        return f"<Provider {self.name}>"

class Review(Model):

    """Container for user review of business.

    Attributes:
        id (int): id of indiviudal review, db primary key
        timestamp (DateTime): date that review entered into db.
                              set automatically.
        user_id (int): id of User that created the review
        provider_id (int): id of provider/business that is being reviewed
        category_id (int): id of category given to review
        rating (int): numeric rating between 1 (low) and 5 (high) to rate quality/satisfaction
        cost (int): numeric rating between 1 (low) and 5 (high) to rate how
                    expensive business is relative to others
        description (str): short description of service being reviewed (ie. AC tuneup)
        service_date (Date): date that reviewers interaction with business took
                             place
        comments (str): full review of business
        pictures (list): list of image files associated with review
        provider (Provider): Provider/Business (object) assoc with provider_id
        user (User): User (object) assoc with user_id
        category (Category): Category (object) associated with category_id

    Methods:
        search: returns list of reviews associated with given provider based on 
                provider id and social filter
    Relationships:
        Parent of: Picture
        Child of: Category, User, Provider
    """

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id",
                                                      ondelete="cascade"),
                            nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"),
                            nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    _description = db.Column(db.String(120))
    service_date = db.Column(db.Date)
    _comments = db.Column(db.Text)

    pictures = db.relationship("Picture", backref="review",
                               cascade="all, delete-orphan",
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

    @classmethod
    def search(cls, providerId, filter):
        """Searches for reviews based on provider id and social filters.
        
        Args:
            providerId (int): provider id from database
            filter (dict): determines whether to only include reviews
                                 that have been reviewed by friends or members
                                 users groups
        Returns:
            list of review objects
        
        """
        # base filter and join args
        filter_args = [Provider.id == providerId]
        join_args = [Review.provider, Review.user]
        friendsFilter = User.friends.contains(current_user)
        groups = [g.id for g in current_user.groups]
        groupsFilter = and_(Group.id.in_(groups), User.id != current_user.id)
        if filter['friends_filter'] is True and filter['groups_filter'] is False:
            filter_args.append(friendsFilter)
        elif filter['groups_filter'] is True and filter['friends_filter'] is False:
            join_args.extend([User.groups])
            filter_args.extend(groupsFilter)
        elif filter['groups_filter'] is True and filter['friends_filter'] is True:
            filter_args.append(or_(groupsFilter, friendsFilter))
        reviews = (db.session.query(Review).join(*join_args)
                                           .filter(*filter_args)
                                           .all())
        return reviews


class Picture(Model):
    """Class to define picture table in db, to be linked with reviews.
    picture_path - filters['location'] of picture in file storage system
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
    """Groups (social, religious, sports, etc.) that user can belong to.
    
    Attributes:
        id (int): primary key of group in db
        name (str): name of group, unique
        description (str): short description of group
        admin_id (int): user_id of group_admin
        members (list): list of Users that are members of the group
        admin (User): User object associated with admin_id
        join_requests (list): GroupRequests (request to join group) that are
                              active for the group
    Methods:
        None

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
        self._name = name

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
    
    @classmethod
    def search(cls, filters):
        """Search groups for groups match search query."""
        memberCheck = exists().where(cls.members.contains(current_user)).label("membership")
        query_args = [cls.id, cls.name, cls.description, memberCheck]
        join_args = []
        outerjoin_args = []
        filter_args = [cls.name.ilike(f"%{filters['name']}%")]
        sort_arg = [cls.name]
        limit = None
        groups = (db.session.query(*query_args)
                                     .join(*join_args)
                                     .outerjoin(*outerjoin_args)
                                     .filter(*filter_args)
                                     .group_by(cls.id)
                                     .order_by(*sort_arg)
                                     .limit(limit)
                                     .all())      
        return groups        