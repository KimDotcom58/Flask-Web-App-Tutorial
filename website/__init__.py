from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "app.db"

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .stock_views import stock_views
    from .crypto_views import crypto_views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(stock_views, url_prefix='/stocks')
    app.register_blueprint(crypto_views, url_prefix='/cryptos')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
        app.app_context().push()
        populate_database()


def populate_database():
    from .database import database

    database.populate_strategies()
    database.populate_filters()
    database.populate_markets()
    database.populate_trading()
    database.populate_stocks()
    database.populate_stock_prices()
    database.populate_cryptos()
    database.populate_crypto_prices()
    database.populate_user()

    print("Populated Database!")


