from app import db, login
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(64), nullable=False, index=True)
    state_short = db.Column(db.String(24), index=True)
    addresses = db.relationship("Address", back_populates="state", lazy=True)

    def _repr__(self):
        return f"<State {self.state}>"


class Address(db.Model):
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _repr__(self):
        return f"<User {self.username}>"

    def _repr__(self):
        return f"<Zip {self.zip}>"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#many to many table linking providers to multiple categories
category_provider_table = Table('association', db.Model.metadata,
    Column('category_id', Integer, ForeignKey('category.id')), 
    Column('provider_id', Integer, ForeignKey('provider.id')))

class Category(db.Model):
    """List service categories."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    providers = db.relationship("provider", secondary=category_provider_table, 
                              backref="categories")

class Provider(db.Model):
    """Create service provider record."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    telephone = db.Column(db.String(24), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    address = db.relationship("Address", backref="provider", lazy=True)
