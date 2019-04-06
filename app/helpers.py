from app import db
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

def dbAdd(item):
    """Add item to db and handle errors
    item: SQLALCHEMY model class from models.py.
    """
    try:
        db.session.add(item)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        print("caught an integrity error")
        raise

    finally:
        db.session.close()


    

