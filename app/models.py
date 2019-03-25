from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class State(db.Model):
    """States used in db."""
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(64), nullable=False, index=True)
    state_short = db.Column(db.String(24), index=True)
    addresses = db.relationship("Address", back_populates="state", lazy=True)

    def _repr__(self):
        return f"<State {self.state}>"


class Address(db.Model):
    """Addresses used for users and providers."""
    id = db.Column(db.Integer, primary_key=True)
    line1 = db.Column(db.String(128))
    line2 = db.Column(db.String(128))
    zip = db.Column(db.String(20), index=True)
    city = db.Column(db.String(64), index=True)
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"))
    state = db.relationship("State", back_populates="addresses", lazy=True)

    def __repr__(self):
        return f"<Address {self.line1}, {self.city}, {self.state}>"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    address = db.relationship("Address", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _repr__(self):
        return f"<User {self.username}>"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# many to many table linking providers to multiple categories
category_provider_table = db.Table('association', db.Model.metadata,
    db.Column('category_id', db.Integer, db.ForeignKey('category.id')), 
    db.Column('provider_id', db.Integer, db.ForeignKey('provider.id')))


class Category(db.Model):
    """List service categories."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    providers = db.relationship("Provider", secondary=category_provider_table, 
                              backref="categories")
    reviews = db.relationship("Review", backref="category", lazy=True)

    def _repr__(self):
        return f"<Category {self.category}>"


class Provider(db.Model):
    """Create service provider record."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    telephone = db.Column(db.String(24), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    address = db.relationship("Address", backref="provider", lazy=True)
    reviews = db.relationship("Review", backref="provider", lazy=True)

    def _repr__(self):
        return f"<Provider {self.name}>"


# many to many table linking pictures with reviews
review_picture = db.Table('association', db.Model.metadata,
    db.Column('review_id', db.Integer, db.ForeignKey('review.id')), 
    db.Column('picture_id', db.Integer, db.ForeignKey('picture.id')))


class Review(db.Model):
    """Class to create define review table in db."""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    rating = db.Column(db.Integer)
    description = db.Column(db.String(120))
    service_date = db.Column(db.Date)
    comments = db.Column(db.Text)
    
    pictures = db.relationship("Picture", secondary=review_picture, 
                               backref="review")

    def _repr__(self):
        return f"<Rating {self.id}, {self.date}>"

class Picture(db.Model):
    """Class to define picture table in db, to be linked with reviews.""""
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.Blob)

