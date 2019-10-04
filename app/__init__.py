import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

from flask import Flask

import config
from app.extensions import csrf, db, login, mail, migrate
from app.models import User, Address, State, Category, Review, Provider, Group


def register_extensions(app):
    """Register extension with app."""
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)


def register_blueprints(app):
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.relationship import bp as relat_bp
    app.register_blueprint(relat_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


def register_shell(app):
    """Register shell context objects."""

    def shell_context():
        namespace = {"User":User, "Address":Address, "State":State, "Category": 
                     Category, "Review": Review, "Provider": Provider,
                     "Group": Group, "db": db}
        return  namespace

    app.shell_context_processor(shell_context)


def configure_logging(app):
    """Configure logging for app."""
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Website Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/Ask.log', maxBytes=10240,
                                            backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('Ask startup')


def create_app(configClass=None):
    """Application factor."""
    app = Flask(__name__)
    if configClass is None:
        if app.config['ENV'] == 'production':
            app.config.from_object(config.ProductionConfig)
        else:
            app.config.from_object(config.DevelopmentConfig)
    else:
        app.config.from_object(configClass)
    register_extensions(app)
    register_blueprints(app)
    configure_logging(app)
    register_shell(app)
    return app

from app import database
