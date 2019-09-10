"""Database configurations and customization."""

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

from app.extensions import db, login


# # sets foreign keys to on for sqlite db connection
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations.
    Source: """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            if value != getattr(self, attr):
                setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
                raise
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


# customized base class to use when initializing db in extensions
class Model(CRUDMixin, db.Model):
    """Subclass to add in CRUDMixin functionality to db.Model base class."""

    __abstract__ = True

# define Flask_Login user loader
@login.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))

