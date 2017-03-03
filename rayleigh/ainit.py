# -*- coding: UTF-8 -*-
# encoding = utf-8
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config
import os

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(app):
    app.config.from_object(config[os.getenv('FLASK_CONFIG') or 'default'])
    config[os.getenv('FLASK_CONFIG') or 'default'].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/main')

    return app
