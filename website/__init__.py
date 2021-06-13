from flask import Flask
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# set configuration values
class Scheduler_config:
    SCHEDULER_API_ENABLED = True

#instantiate database
db = SQLAlchemy()
DB_NAME = "app.db"

scheduler = APScheduler()

def create_app():

    # intantiate app
    app = Flask(__name__)
    
    app.config.from_object(Scheduler_config())

    #instatiate scheduler
    scheduler.init_app(app)

    from .scheduler_tasks import scheduled_tasks
    scheduled_tasks()

    scheduler.start()

    # app settings, path to database
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # 'connect' app to database
    db.init_app(app)

    # Blueprints
    from .views import views
    from .stock_views import stock_views
    from .crypto_views import crypto_views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(stock_views, url_prefix='/stocks')
    app.register_blueprint(crypto_views, url_prefix='/cryptos')
    app.register_blueprint(auth, url_prefix='/')

    # If database does not exist, it will be created
    create_database(app)

    # instantiate login manager
    from .models import User
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # return app and scheduler
    return [app, scheduler]


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


