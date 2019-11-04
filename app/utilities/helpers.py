import functools

from io import BytesIO
import os
from pathlib import Path
import requests
from urllib.parse import urlparse

from flask import flash, Markup, session, url_for, current_app
from flask_login import current_user
from PIL import Image
from wtforms.widgets.core import RadioInput

from app.utilities.forms import RadioInputDisabled



def thumbnail_from_buffer(buffer, size, name, path):
    """Save thumbnail from submitted picture.
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
    thumb.save(os.path.join(path, name))
    return None


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


def disableForm(form):
    """Disable all fields in form."""
    disabled = {"disabled": True}
    for field in form:
        if field.type == "FormField":
            disableForm(field)
        elif field.type == "RadioField":
            field.option_widget = RadioInputDisabled()
        else:
            kw_update(field, disabled)

def listToString(items):
    """Converts list to string seperated by appropriate , and & .
    
    Args:
        items (list): list of strings to be joined into a string
    Returns:
        string
    """
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} & {items[1]}"
    else:
        return f'{", ".join(items[:-1])} & {items[-1]}'
    

def url_parse(url):
    u = urlparse(url)
    if u.scheme != "" and u.netloc != "":
        url = f"{u.scheme}://{u.netloc}{u.path}"
        url_string = f"{u.netloc}{u.path}"
    elif u.scheme == "" and u.netloc != "":
        url = f"http://{u.netloc}{u.path}"
        url_string = f"{u.netlock}{u.path}"
    else:
        url = f"http://{u.path}"
        url_string = u.path
    return (url, url_string)  

def url_check(url):
    url = url_parse(url)[0]
    headers = {
        "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException as e:
        print(e)
        return False

