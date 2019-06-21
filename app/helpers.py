from app import db
from flask import flash, Markup, session, url_for
from flask_login import current_user
import functools
from io import BytesIO
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


def dbUpdate():
    """Update db and handle errors
    item: SQLALCHEMY model class from models.py.
    """
    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        print("caught an integrity error")
        raise


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
        f = filename.rsplit(".",2)
        counter += 1
        filename = f"{f[0]}_{counter}.{f[1]}"
        name_check(path, filename, counter)
    elif not exists:
        return filename
    return filename


def pagination_urls(pag_object, endpoint, pag_args):
    """Generates pagination urls for paginated information.
    Inputs:
    pag_object: paginated query object.
    endpoint: endpoint to include in url
    pag_args: args to include in pag_url query string.
    """

    pag_args = dict(pag_args)
    for k in ['submit', 'page']:
        if k in pag_args:
            del pag_args[k]
    pag_dict = {}
    pag_dict['next'] = url_for(endpoint, page=pag_object.next_num, **pag_args)\
                       if pag_object.has_next else None
    pag_dict['prev'] = url_for(endpoint, page=pag_object.prev_num, **pag_args)\
                       if pag_object.has_prev else None
    pag_dict['pages'] = []
    for i in range(pag_object.pages):
        pag_dict['pages'].append((i + 1, url_for(endpoint, page=i + 1, 
                                                 **pag_args)
                                 ))
    return pag_dict


def email_verified(func):
    """Flash message reminding user to verify email address."""
    @functools.wraps(func)
    def wrapped_function(*args, **kwargs):
        
        if current_user.is_anonymous:
            pass
        else:
            if not current_user.email_verified and not session.get('email_verification_sent'):
                flash(Markup("Email address not yet verified. Please check email and "
                "confirm email address."
                "  <a href=" + url_for('auth.email_verify_request') + ">Click "
                "to request new link.</a>"))
            # update email_ver_sent to true to allow reminder to flash on next page
            session['email_verification_sent'] = False    
        return func(*args, **kwargs)
    return wrapped_function


def kw_update(field, new_kw):
    """Update render_kw in form."""
    if field.render_kw is not None:
        field.render_kw.update(new_kw)
    else:
        field.render_kw = new_kw


def disable_form(form):
    """Disable all fields in form."""
    disabled = {"disabled": "disabled"}
    for field in form:
        if field.type == "FormField":
            disable_form(field)
        elif field.type == "RadioField":
            for subfield in field:
                kw_update(subfield, disabled)
        else:
            kw_update(field, disabled)






