import os, sys, base64

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


class Config:
    APP_NAME = os.environ.get('APP_NAME') or 'Flask-Base'
    # Spotify Configs
    CLIENT_ID = os.environ.get('CLIENT_ID') or ''
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET') or ''
    PRE_KEY = CLIENT_ID + ':' + CLIENT_SECRET
    AUTHORIZATION = 'Basic ' + base64.b64encode(PRE_KEY.encode()).decode()

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PROD')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')

    CLIENT_URL = os.environ.get('DEV_CLIENT_URL') or \
        'http://127.0.0.1:5000'

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN DEBUG MODE. \
            YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL') or \
        ''

    CLIENT_URL = os.environ.get('CLIENT_URL')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Handle proxy server track_headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'heroku': HerokuConfig,
}
