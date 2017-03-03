# -*- coding: UTF-8 -*-
# encoding = utf-8
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PASSWORD'
    # SECRET_KEY = 'qiuzihe654321'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = os.environ.get('MAIL_USERNAME')
    FLASKY_MAIL_SENDER = 'htszdm@sina.com'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_ADMIN = 'htszdm@sina.com'
    FLASKY_POSTS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_USERNAME = 'htszdm@sina.com'
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PASSWORD = 'qiuzihe654321'


class TestingConfig(Config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
