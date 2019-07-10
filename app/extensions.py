from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData

from config import Config


# metadata used for dbinitialization
metadata = MetaData(naming_convention=Config.SQLALCHEMY_NAMING_CONVENTION)
db = SQLAlchemy(metadata=metadata)

migrate = Migrate()
login = LoginManager()
login.login_view = "auth.welcome"
login.login_message = 'Please log in to access the requested page.'
csrf = CSRFProtect()
mail = Mail()
