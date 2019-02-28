class Config(object):
    DEBUG = True
    SECRET_KEY = "743b342c0cdb6f946dada260a118df296bd3266904b718db"

    SECURITY_PASSWORD_SALT = '743b342c0cdb6f946dada260a118df296bd3266904b718db'

    #email server
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEBUG = True
    MAIL_USERNAME = "velvenkatesh17@gmail.com"
    MAIL_PASSWORD = "Cricket@vel77"


class ProductionConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DB_NAME = 'tasks'
    DB_HOST = 'localhost'
    DB_PORT = 27017
