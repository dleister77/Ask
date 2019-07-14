from datetime import datetime, date
from operator import attrgetter
import re
from string import capwords

from flask import current_app, render_template
from flask_login import UserMixin, current_user
import jwt
from sqlalchemy import CheckConstraint
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from threading import Thread
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import Model
from app.extensions import db
from app.utilities.email import decode_token, get_token, send_email
from app.utilities.geo import geocode, get_distance, get_geo_range



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

# many to many table linking pictures with providers with service area locations
# provider_location = db.Table('provider_location', db.Model.metadata,
#     db.Column('provider_id', db.Integer, db.ForeignKey('provider.id')),
#     db.Column('location_id', db.Integer, db.ForeignKey('location.id')))

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
    _line1 = db.Column(db.String(128))
    _line2 = db.Column(db.String(128))
    zip = db.Column(db.String(20), index=True)
    _city = db.Column(db.String(64), index=True, nullable=False)
    unknown = db.Column(db.Boolean, default=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id",
                                                  ondelete="CASCADE"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id",
                                                      ondelete="CASCADE"))
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), nullable=False)
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)

    __table_args__ = (
        CheckConstraint('provider_id IS NOT NULL OR user_id IS NOT NULL',
                        name="chk_address_fks"),
        # CheckConstraint('_line1 IS NOT NULL AND zip IS NOT NULL OR unknown == 1',
        #                 name='chk_line1zipunknown')
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
    
    @hybrid_property
    def coordinates(self):
        return (self.latitude, self.longitude)

    def get_coordinates(self):
        """Get latitude and longitude for given address and store in db."""
        address = f"{self. line1}, {self.city}, {self.state.state_short} {self.zip}"
        latitude, longitude = geocode(address)
        self.update(latitude=latitude, longitude=longitude)
        return None

    def __repr__(self):
        return f"<Address {self.line1}, {self.city}, {self.state}>"


# def Location(Model):
#     """US cities and States used to populate service area locations.
#     Relationships:
#     Many to Many: Providers
#     """
#     id = db.Column(db.Integer, primary_key=True)
#     city = db.Column(db.String(64))
#     state = db.Column(db.String(64))
#     state_short = db.Column(db.String(64))

#     def __repr__(self):
#         return f"<Location {self.city} {self.state}>"


class User(UserMixin, Model):
    """Creates user class.
    Relationships:
        Parent of: Reviews, Address, FriendRequest
        Child of:
        ManytoMany: Group, User(friends)
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
    email_token_key = 'verify_email'
    password_token_key = 'reset_password'

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

    def _get_reset_password_token(self):
        """Get password reset token."""
        payload = {self.password_token_key: self.id}
        expiration = 10/(60*24)  # 10 minutes
        return get_token(payload, expiration)

    def send_password_reset_email(self):
        token = self._get_reset_password_token()
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
            id = decode_token(token, User.password_token_key)
        except:
            return
        return User.query.get(id)

    def _get_email_verification_token(self):
        """Get jwt token for email address verification."""
        payload = {self.email_token_key: self.id}
        expiration = 10
        return get_token(payload, expiration)

    def send_email_verification(self):
        """Send email to request email verification."""
        token = self._get_email_verification_token()
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
            id = decode_token(token, User.email_token_key)
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
    date_sent = db.Column(db.Date, index=True, nullable=False,
                          default=date.today())
    token_key = 'request'


    def __repr__(self):
        return f"<FriendRequest {self.requestor.full_name} {self.requested_friend.full_name}>"

    def get_request_token(self):
        """Get friend request token."""
        payload = {self.token_key: self.id}
        expiration = None
        return get_token(payload, expiration)

    def send(self):
        """Send friend request email and update FriendRequest table."""
        token = self.get_request_token()
        send_email('Ask a Neighbor: Friend Verification',
                sender=current_app.config['ADMINS'][0],
                recipients=[self.requested_friend.email],
                text_body=render_template('relationship/email/friend_request.txt',
                                            user=self.requested_friend,
                                            friend=self.requestor,
                                            token=token),
                html_body=render_template('relationship/email/friend_request.html',
                                            user=self.requested_friend,
                                            friend=self.requestor,
                                            token=token))
        return None

    @staticmethod
    def verify_token(token):
        """Check friend request token and returns request if valid and error
           if invalid."""
        try:
            request_id = decode_token(token, FriendRequest.token_key)
            request = FriendRequest.query.get(request_id)
        except:
            request = None
        return request

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
    date_sent = db.Column(db.Date, index=True, nullable=False, default=date.today())
    token_key = 'request'

    def get_request_token(self):
        """Get group request token."""
        payload = {self.token_key: self.id}
        expiration = None
        return get_token(payload, expiration)

    def send(self):
        """Send group admin request to join & update GroupRequest table."""
        # create group join request
        token = self.get_request_token()
        send_email('Ask a Neighbor: Group Join Request',
                sender=current_app.config['ADMINS'][0],
                recipients=[self.group.admin.email],
                text_body=render_template('relationship/email/group_request.txt',
                                            user=self.group.admin, group=self.group,
                                            new_member=self.requestor, token=token),
                html_body=render_template('relationship/email/group_request.html',
                                            user=self.group.admin, group=self.group,
                                            new_member=self.requestor, token=token))
        return None

    @staticmethod
    def verify_token(token):
        """Check group request token and returns GroupRequest if valid and error
           if invalid."""
        try:
            request_id = decode_token(token, GroupRequest.token_key)
            request = GroupRequest.query.get(request_id)
        except:
            request = None
            raise
        return request



    def __repr__(self):
        return f"<GroupRequest {self.requestor.full_name} {self.group.name}>"

    @staticmethod
    def get_pending(user):
        """Return pending approval requests user is admin for."""
        pending = GroupRequest.query.join(Group)\
                                    .filter(Group.admin_id == user.id).all()
        return pending
 
class Sector(Model):
    """Sector that categories are a member of.
    Relationships:
        Parent of: category
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)

    categories = db.relationship("Category", backref=backref("sector",
                                                             uselist=False))

    @staticmethod
    def list():
        """Query db to populate state list on forms."""
        if current_app.config['TESTING'] == True:
            list = current_app.config['TEST_SECTOR']
        else:
            try:
                list = [(s.id, s.name) for s in Sector.query.order_by("name")]
            except OperationalError:
                list = [(1, "Test")]
        return list

    def __repr__(self):
        return f"<Sector {self.name}>"


class Category(Model):
    """List service categories.
    Relationships:
        Parent of: Review
        Many to Many: Provider
        Child of: Sector
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"))
    # service_area_required = db.Column(db.Boolean, default=False)

    providers = db.relationship("Provider", secondary=category_provider_table,
                                backref="categories")
    reviews = db.relationship("Review", backref="category")

    @staticmethod
    def list(sector_id):
        """Query db to populate form category list based on selected sector."""
        if current_app.config['TESTING'] == True:
            list = current_app.config['TEST_CATEGORIES']
        else:
            try:
                sector = (Sector.query.get(sector_id))
                list = (Category.query.filter(Category.sector == sector)
                                          .order_by(Category.name)).all()
                list = [(category.id, category.name) for category
                                in list]                
                
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
        Many to Many: category, locations
    
    Methods:
    list: generate list of provider id and name based on category.
    autocomplete: generate autocomplete data based on already entered criteria
    search: generate list of providers based on submitted form data
    profile: return tuple of provider summary statistics / provider object
            based on social filter
    profile_reviews: return provider profile reviews based on social filter.
    """
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    _telephone = db.Column(db.String(24), unique=True, nullable=False)

    address = db.relationship("Address", backref="provider", uselist=False,
                              passive_deletes=True)
    reviews = db.relationship("Review", backref="provider")
    # service_area = db.relationship("Location", secondary="provider_location",
    #                                backref = "providers")

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
        Inputs:
        category_id: category to filter by
        format: output format, either 'dict' or 'tuple'
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
        return provider_list

    @staticmethod
    def autocomplete(name, category_id, city, state_id, limit=10):
        """Returns list of providers to populate autocomplete."""
        filter_args = [Provider.name.ilike(f"%{name}%")]
        join_args = [Provider.address]
        if city:
            filter_args.append(Address.city.ilike(f"%{city}%"))
        if state_id:
            filter_args.append(Address.state_id == state_id)
        if category_id:
            category = Category.query.get(category_id)
            filter_args.append(Provider.categories.contains(category))
        providers = Provider.query.join(*join_args).filter(*filter_args)\
                                    .order_by(Provider.name).limit(limit).all()
        if providers == []:
            name = name.replace("", "%")
            providers = Provider.query.join(*join_args).filter(*filter_args)\
                                .order_by(Provider.name).limit(limit).all()
        return providers

    @classmethod
    def search(cls, form, range=30):
        """Determine which method to call."""
        category = Category.query.get(form.category.data)
        origin = current_user.address.coordinates
        min_long, max_long, min_lat, max_lat = get_geo_range(origin, range)
        sort_criteria = form.sort.data
        filtered = form.reviewed_filter.data is True\
                   or form.friends_filter.data is True\
                   or form.groups_filter.data is True
        query_args = [Provider]
        filter_args = [Provider.categories.contains(category),
                       Address.longitude > min_long,
                       Address.longitude < max_long,
                       Address.latitude > min_lat,
                       Address.latitude < max_lat]
        join_args = [Provider.address]
        if form.name.data is not None:
            name = f"%{form.name.data}%"
            filter_args.append(Provider.name.ilike(name))
        if filtered:
            query_args.extend([func.avg(Review.rating).label("average"),
                               func.avg(Review.cost).label("cost"),
                               func.count(Review.id).label("count")])
            join_args.extend([Provider.reviews, Review.user])
            if form.friends_filter.data is True:
                filter_args.append(User.friends.contains(current_user))
            if form.groups_filter.data is True:
                groups = [g.id for g in current_user.groups]
                filter_args.extend([Group.id.in_(groups), User.id != current_user.id])
                join_args.extend([User.groups])
        providers = (db.session.query(*query_args)
                                     .join(*join_args)
                                     .filter(*filter_args)
                                     .group_by(Provider.name)
                                     .order_by(Provider.name)
                                     .all())
        cls._sort(providers, sort_criteria, filtered, origin)
        
        return providers

    def profile(self, filter):
        """Return tuple of provider object with review summary information(avg/count)
        form: boolean form with friend/group filters
        """
        # base filter and join args
        filter_args = [Provider.id == self.id]
        join_args = [Review.provider, Review.user]
        # update filter and joins for relationship filters
        if filter['friends_filter'] is True:
            filter_args.append(User.friends.contains(current_user))
        if filter['groups_filter'] is True:
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
        if filter['friends_filter'] is True:
            filter_args.append(User.friends.contains(current_user))
        if filter['groups_filter'] is True:
            groups = [g.id for g in current_user.groups]
            join_args.extend([User.groups])
            filter_args.extend([Group.id.in_(groups), User.id != current_user.id])
        reviews = (db.session.query(Review).join(*join_args)
                                           .filter(*filter_args))
        return reviews
    
    @classmethod
    def _sort(cls,results, sort_criteria, filtered, origin):
        """Sort search results.
        Inputs:
           search_results: list of providers or providers/summary stat tuples
           sort_criteria: criteria to sort by (either distance, rating or name)
           filtered: whether results only include providers with reviews
           origin: starting point for distance calculations
        """
        if filtered:
            if sort_criteria == 'distance':
                results.sort(key=lambda provider:
                get_distance(origin, provider[0].address.coordinates))
            elif sort_criteria == 'rating':
                results.sort(key=attrgetter('average'), reverse=True)
        else:
            if sort_criteria == 'distance':
                results.sort(key=lambda provider:
                get_distance(origin, provider.address.coordinates))
            elif sort_criteria == 'rating':
                results.sort(key=attrgetter('average_rating'), reverse=True)
        return None

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
