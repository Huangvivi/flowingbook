from flask import Flask
from flask_login import LoginManager
# from flowingbook.views import views
from flowingbook.models.book import db
from flask_mail import Mail
from flowingbook.utils.limiter import Limiter

login_manager = LoginManager()
mail = Mail()
limiter = Limiter()


def create_app():
    app = Flask(__name__)
    app.app_context()
    app.config.from_object("config")
    app.config.from_object("secure")
    register_blueprint(app)
    db.init_app(app)
    db.create_all(app=app)
    # with app.app_context():
    #     db.create_all()

    login_manager.init_app(app)

    # 当未登录用户访问需要登录后才能访问的页面时自动跳转的页面
    login_manager.login_view = 'views.login'
    login_manager.login_message = '请先登录或注册'

    mail.init_app(app)

    return app


def register_blueprint(app):
    from flowingbook.views import views
    app.register_blueprint(views)

