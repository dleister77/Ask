from app import db, login
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash


class State(db.Model):
    """States used in db.
    Relationships:
        Parent of: Address    
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    state_short = db.Column(db.String(24), index=True)
    addresses = db.relationship("Address", backref="_state")

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
    
    @line1.setter
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
    Methods:
        set_password: Store submitted password as hash.
        check_password: Compares hashed submitted password to store password hash.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    _first_name = db.Column(db.String(64), index=True)
    _last_name = db.Column(db.String(64), index=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    address = db.relationship("Address", backref="user")
    reviews = db.relationship("Review", backref="user")

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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# many to many table linking providers to multiple categories
category_provider_table = db.Table('category_provider', db.Model.metadata,
    db.Column('category_id', db.Integer, db.ForeignKey('category.id')), 
    db.Column('provider_id', db.Integer, db.ForeignKey('provider.id')))


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
    telephone = db.Column(db.String(24), unique=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    address = db.relationship("Address", backref="provider")
    reviews = db.relationship("Review", backref="provider")

    @hybrid_property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name.title()

    def __repr__(self):
        return f"<Provider {self.name}>"


# many to many table linking pictures with reviews
review_picture = db.Table('review_picture', db.Model.metadata,
    db.Column('review_id', db.Integer, db.ForeignKey('review.id')), 
    db.Column('picture_id', db.Integer, db.ForeignKey('picture.id')))


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
        self._description = description.capitalize()

    @hybrid_property
    def comments(self):
        return self._comments
    
    @comments.setter
    def comments(self, comments):
        self._comments = comments.capitalize()

    def _repr__(self):
        return f"<Rating {self.provider}, {self.rating}>"

class Picture(db.Model):
    """Class to define picture table in db, to be linked with reviews.
    Relationships:
        Child of: Review
    """
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.BLOB)

