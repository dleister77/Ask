from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData

app = Flask(__name__)
app.config.from_object(Config)
metadata = MetaData(naming_convention=Config.SQLALCHEMY_NAMING_CONVENTION)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"
csrf = CSRFProtect(app)

from app import routes, models
