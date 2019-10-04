
import os
import dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "Mohren10$"

    #sql alchemy info
    SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"}

    #file upload info
    UPLOAD_FOLDER = 'photos'
    MEDIA_FOLDER = os.path.join('photos')

    #Mail / logging items
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['djl.webprojects@gmail.com']

    #API Keys
    GEOCODIO_API_KEY = os.environ.get('GEOCODIO_API_KEY')
    TAMU_API_KEY = os.environ.get('TAMU_API_KEY')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
        
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_PROTECTION = "strong"
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PER_PAGE = 10

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_PROTECTION = "strong"
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PER_PAGE = 2

class TestConfig(Config):
    TESTING = True
    SERVER_NAME = 'localhost.localdomain'
    SQLALCHEMY_DATABASE_URI =  os.environ.get('TEST_DATABASE_URL')
    PER_PAGE = 2
    WTF_CSRF_ENABLED = False
    MEDIA_FOLDER = os.path.join(basedir, 'instance', 'tests', 'photos')
    TEST_STATES = [(2, "New York"),(1, "North Carolina")]
    TEST_CATEGORIES = [(1, "Electrician"), (2, "Plumber")]
    TEST_SECTOR = [(1, "Home Services")]
    TEST_USER = {"username": "jjones", "password": "password"}