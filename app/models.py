from app import db, login
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(64), nullable=False, index=True)
    addresses = db.relationship("Address", back_populates="city",  lazy=True)

    def _repr__(self):
        return f"<City {self.city}>"

class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(64), nullable=False, index=True)
    state_short = db.Column(db.String(24), index=True)
    addresses = db.relationship("Address", back_populates="state", lazy=True)

    def _repr__(self):
        return f"<State {self.state}>"

class Zip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zip = db.Column(db.String(20), index=True, unique=True)
    addresses = db.relationship("Address", back_populates="zip", lazy=True)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line1 = db.Column(db.String(128))
    line2 = db.Column(db.String(128))
    zip_id = db.Column(db.Integer, db.ForeignKey("zip.id"))
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"))
    zip = db.relationship("Zip", back_populates="addresses", lazy=True)
    city = db.relationship("City", back_populates="addresses", lazy=True)
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