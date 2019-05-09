from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy, Model
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from sqlalchemy import MetaData


class AskModel(Model):
    """Added functionality to standard flask-sa db.model."""
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if getattr(self, k) != v:
                setattr(self, k, v)

metadata = MetaData(naming_convention=Config.SQLALCHEMY_NAMING_CONVENTION)
db = SQLAlchemy(metadata=metadata, model_class=AskModel)
# db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.index"
login.login_message = 'Please log in to access the request page.'
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.relationship import bp as relat_bp
    app.register_blueprint(relat_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # if not app.debug and not app.testing:
    #     if app.config['MAIL_SERVER']:
    #         auth = None
    #         if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
    #             auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    #         secure = None
    #         if app.config['MAIL_USE_TLS']:
    #             secure = ()
    #         mail_handler = SMTPHandler(
    #             mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
    #             fromaddr='no-reply@' + app.config['MAIL_SERVER'],
    #             toaddrs=app.config['ADMINS'], subject='Website Failure',
    #             credentials=auth, secure=secure)
    #         mail_handler.setLevel(logging.ERROR)
    #         app.logger.addHandler(mail_handler)
    #     if not os.path.exists('logs'):
    #         os.mkdir('logs')
    #     file_handler = RotatingFileHandler('logs/Ask.log', maxBytes=10240,
    #                                         backupCount=10)
    #     file_handler.setFormatter(logging.Formatter(
    #         '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    #     file_handler.setLevel(logging.INFO)
    #     app.logger.addHandler(file_handler)
    #     app.logger.info('Ask startup')
    
    return app


from app import models
