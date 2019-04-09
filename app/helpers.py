from app import db
from flask_login import current_user
from io import StringIO, BytesIO
import os
from pathlib import Path
from PIL import Image
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

def thumbnail_from_buffer(buffer, size, name, path):
    """save thumbnail from submitted picture.
    buffer: incoming picture data
    size: tuple, size in pixels to convert picture to.
    name: original file name
    path: file path to save picture to.
    returns thumbnail filename as string
    """
    buffer.seek(0)
    bufferdata = buffer.read()
    bio = BytesIO(bufferdata)
    thumb = Image.open(bio)
    thumb.thumbnail(size)
    f = name.rsplit(".", 2)
    thumb_name = f"{f[0]}_thumbnail.{f[1]}"
    thumb.save(os.path.join(path, thumb_name))
    return (thumb_name)
    
def name_check(path, filename, counter=0):
    """Checks if file already exists, increments by number to be unique.
    Inputs:
    path: path to directory where file will be saved.
    filename: name of file
    counter: counter which determines number to be added to filename

    returns: final unique filename
    """
    p = Path(os.path.join(path, filename))
    exists = p.is_file()
    if exists:
        print(f"Exists number {counter}")
        f = filename.rsplit(".",2)
        counter += 1
        filename = f"{f[0]}_{counter}.{f[1]}"
        name_check(path, filename, counter)
    elif not exists:
        print("not exists")
        return filename
    return filename


