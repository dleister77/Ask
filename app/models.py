from app import db, login
from app.email import send_email
from datetime import datetime, date
from flask import current_app, render_template
from flask_login import UserMixin, current_user
import jwt
import re
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from string import capwords
from time import time
from werkzeug.security import check_password_hash, generate_password_hash

# many to many table linking users with groups
user_group = db.Table('user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')), 
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')))

# many to many table linking providers to multiple categories
category_provider_table = db.Table('category_provider', db.Model.metadata,
    db.Column('category_id', db.Integer, db.ForeignKey('category.id')), 
    db.Column('provider_id', db.Integer, db.ForeignKey('provider.id')))

# many to many table linking pictures with reviews
review_picture = db.Table('review_picture', db.Model.metadata,
    db.Column('review_id', db.Integer, db.ForeignKey('review.id')), 
    db.Column('picture_id', db.Integer, db.ForeignKey('picture.id')))

# many to many table linking pictures with users with friends
user_friend = db.Table('user_friend', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')), 
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id')))


class State(db.Model):
    """States used in db.
    Relationships:
        Parent of: Address    
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    state_short = db.Column(db.String(24), index=True)
    addresses = db.relationship("Address", backref="state")

    def __repr__(self):
        return f"<State {self.name}>"


class Address(db.Model):
    """Addresses used for users and providers.
    Relationships:
        Parent of:
        Child of: State, User, Provider
    """
    id = db.Column(db.Integer, primary_key=True)
    _line1 = db.Column(db.String(128))
    _line2 = db.Column(db.String(128))
    zip = db.Column(db.String(20), index=True)
    _city = db.Column(db.String(64), index=True)
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"))

    @hybrid_property
    def line1(self):
        return self._line1
    
    @line1.setter
    def line1(self, line1):
        self._line1 = line1.title()
    
    @hybrid_property
    def line2(self):
        return self._line2
    
    @line2.setter
    def line2(self, line2):
        self._line2 = line2.title()
        
    @hybrid_property
    def city(self):
        return self._city
    
    @city.setter
    def city(self, city):
        self._city = city.title()    

    def __repr__(self):
        return f"<Address {self.line1}, {self.city}, {self.state}>"


class User(UserMixin, db.Model):
    """Creates user class.
    Relationships:
        Parent of: Address, Reviews
        ManytoMany: Group, User(friends)
    Methods:
        set_password: Store submitted password as hash.
        check_password: Compares hashed submitted password to store password hash.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    _email = db.Column(db.String(120), index=True, unique=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(128))
    password_set_date = db.Column(db.Date, index=True)
    _first_name = db.Column(db.String(64), index=True)
    _last_name = db.Column(db.String(64), index=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    address = db.relationship("Address", backref="user", lazy=False)
    reviews = db.relationship("Review", backref="user")
    friends = db.relationship("User", secondary=user_friend,
                              primaryjoin=(id == user_friend.c.user_id),
                              secondaryjoin=(id == user_friend.c.friend_id),
                              backref="friendsWith")

    @hybrid_property
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self, first_name):
        self._first_name = first_name.title()

    @hybrid_property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, last_name):
        self._last_name = last_name.title()

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
        self.password_hash = generate_password_hash(password)
        self.password_set_date = date.today()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

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
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def get_email_verification_token(self, expires_in=60*60*24*10):
        """Get jwt token for email address verification."""
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    
    def send_email_verification(self):
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

    def _addfriend(self, person):
        """Add friend relationship bi-directionally."""
        self.friends.append(person)
        person.friends.append(self)

    def _addgroup(self, group):
        """Add group relationship."""
        self.groups.append(group)

    def add(self, relation):
        """Determine whether to add group or friend and call approp method."""
        if type(relation) == User:
            self._addfriend(relation)
        elif type(relation) == Group:
            self._addgroup(relation)

    def summary(self):
        """Return user object with review summary information(avg/count)"""
        # need to accomodate zero reviews...joins makes it unable to calc
        summary = (db.session.query(func.avg(Review.rating).label("average"),
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
                                      func.count(Review.id).label("count"))
                               .join(*join_args)
                               .filter(*filter_args)
                               .group_by(Provider.name)
                               .order_by(Provider.name))
        return providers
       
    def __repr__(self):
        return f"<User {self.username}>"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Category(db.Model):
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

    def __repr__(self):
        return f"<Category {self.name}>"


class Provider(db.Model):
    """Create service provider record.
    Relationship:
        Parent of: address, review
        Many to Many: category
    """
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    _telephone = db.Column(db.String(24), unique=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    address = db.relationship("Address", backref="provider")
    reviews = db.relationship("Review", backref="provider")

    @hybrid_property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = capwords(name)
    
    @hybrid_property
    def telephone(self):
        return self._telephone
    
    @telephone.setter
    def telephone(self, telephone):
        self._telephone = re.sub('\D+', '', telephone)

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
                                    func.count(Review.id).label("count"))
                             .join(*join_args)
                             .filter(*filter_args)
                             .first())
        return (self, summary.average, summary.count)

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


class Review(db.Model):
    """Class to create define review table in db.
    Relationships:
        Parent of: Picture
        Child of: Category, User, Provider
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    rating = db.Column(db.Integer)
    _description = db.Column(db.String(120))
    service_date = db.Column(db.Date)
    _comments = db.Column(db.Text)
    
    pictures = db.relationship("Picture", secondary=review_picture, 
                               backref="review")

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


class Picture(db.Model):
    """Class to define picture table in db, to be linked with reviews.
    picture_path - location of picture in file storage system
    Relationships:
        Child of: Review
    """
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(120))
    name = db.Column(db.String(120))
    thumb = db.Column(db.String(120))


class Group(db.Model):
    """Groups that users can belong to.
    Relationships:
        Many to Many: User
        One to one: User/admin
    """
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), index=True, unique=True)
    _description = db.Column(db.String(120))
    admin_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    members = db.relationship("User", secondary=user_group, 
                              backref="groups")
    admin = db.relationship("User", backref="group_admin")

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
