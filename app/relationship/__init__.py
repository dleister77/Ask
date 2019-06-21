from flask import Blueprint

bp = Blueprint('relationship', __name__)

from app.relationship import routes