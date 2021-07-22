from flask import Flask
from flask_login import LoginManager
import website.config as config
import logging
from os import path, environ

from .extensions import scheduler, db, db_name, xtb_api
from .settings import DevelopmentConfig

def create_app():

    def is_debug_mode():
        """Get app debug status."""
        debug = environ.get("FLASK_DEBUG")
        if not debug:
            return environ.get("FLASK_ENV") == "development"
        return debug.lower() not in ("0", "false", "no")

    def is_werkzeug_reloader_process():
        """Get werkzeug status."""
        return environ.get("WERKZEUG_RUN_MAIN") == "true"

    # intantiate app
    app = Flask(__name__)

    # app settings, path to database
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
    app.config.from_object(DevelopmentConfig)

    # 'connect' app to database
    db.init_app(app)

    #instatiate scheduler
    scheduler.init_app(app)

    logging.getLogger("apscheduler").setLevel(logging.INFO)

    with app.app_context():

        # pylint: disable=W0611
        if is_debug_mode() and not is_werkzeug_reloader_process():
            pass
        else:
            from .tasks import task2

            scheduler.start()

        from . import events  # noqa: F401

        from .tasks import task2, task_populate_database, task_strategy_bollinger, task_strategy_opening_breakdown, task_strategy_opening_breakout

        # Blueprints
        from .views import views
        from .stock_views import stock_views
        from .crypto_views import crypto_views
        from .scheduler_views import scheduler_views
        from .auth import auth

        app.register_blueprint(views, url_prefix='/')
        app.register_blueprint(stock_views, url_prefix='/stocks')
        app.register_blueprint(crypto_views, url_prefix='/cryptos')
        app.register_blueprint(scheduler_views, url_prefix='/schedulers')
        app.register_blueprint(auth, url_prefix='/')

        # If database does not exist, it will be created
        create_database(app)

        # scheduler.add_job(
        #     func=task_strategy_opening_breakdown,
        #     trigger="interval",
        #     seconds=10,
        #     id="periodic opening range breakdown",
        #     name="periodic opening range breakdown",
        #     replace_existing=True,
        # )

        # scheduler.add_job(
        #     func=task_strategy_opening_breakout,
        #     trigger="interval",
        #     seconds=10,
        #     id="periodic opening range breakout",
        #     name="periodic opening range breakout",
        #     replace_existing=True,
        # )

        # scheduler.add_job(
        #     func=task_strategy_bollinger,
        #     trigger="interval",
        #     seconds=10,
        #     id="periodic bollinger",
        #     name="periodic bollinger",
        #     replace_existing=True,
        # )

        # scheduler.add_job(
        #     func=task_populate_database,
        #     trigger="cron",
        #     day_of_week='mon-fri',
        #     hour=23,
        #     minute=59,
        #     id="periodic stock populating",
        #     name="periodic stock populating",
        #     replace_existing=True,
        # )
 
         # # CHECK IF MARKET IS OPEN FOR EURUSD
        new = xtb_api.get_trading_hours(['EURCHF'])
        week = [None] * 7
        for symbol in new:
            for day in symbol['trading']:
                fromT = day['fromT']
                hours1 = int(fromT/3600)
                left = fromT - hours1*3600
                if str(hours1) == '0':
                    hours1 = '00'
                minutes1 = str(int(left/60))
                if minutes1 == '0':
                    minutes1 = '00'

                toT = day['toT']
                hours2 = int(toT/3600)
                left = toT - hours2*3600
                if str(hours2) == '0':
                    hours2 = '00'
                minutes2 = str(int(left/60))
                if minutes2 == '0':
                    minutes2 = '00'
                week[day['day']-1] = [f"{hours1}:{minutes1}",f"{hours2}:{minutes2}"]

            for day in week:
                if day == None:
                    number = week.index(day)
                    week[number] = [ "00:00", "00:00"]

            print(week)
    # import degiroapi
    # from degiroapi.product import Product
    # from degiroapi.order import Order
    # from degiroapi.utils import pretty_json

    # degiro = degiroapi.DeGiro()
    # degiro.login("kimbo91", "SifdjObmnk1")

    # degiro.logout()

    # instantiate login manager
    from .models import User
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # return app
    return app

def create_database(app):
    if not path.exists('website/' + db_name):
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
    