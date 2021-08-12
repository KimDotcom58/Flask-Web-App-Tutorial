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

        # from . import events  # noqa: F401

        from .tasks import task2, task_populate_database, task_strategy_bollinger, task_strategy_opening_breakdown, task_strategy_opening_breakout, task_populate_trading

        # Blueprints
        from .views import views
        from .views_alpaca import views_alpaca
        from .views_binance import views_binance
        from .views_xtb import views_xtb
        from .views_scheduler import views_scheduler
        from .auth import auth

        app.register_blueprint(views, url_prefix='/')
        app.register_blueprint(views_alpaca, url_prefix='/alpaca')
        app.register_blueprint(views_binance, url_prefix='/binance')
        app.register_blueprint(views_xtb, url_prefix='/xtb')
        app.register_blueprint(views_scheduler, url_prefix='/schedulers')
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

        scheduler.add_job(
            func=task_populate_database,
            trigger="cron",
            day_of_week='mon-sun',
            hour=00,
            minute=10,
            id="periodic stock populating",
            name="periodic stock populating",
            replace_existing=True
        )

        # scheduler.add_job(
        #     func=task_populate_trading,
        #     trigger="cron",
        #     day_of_week='mon-sun',
        #     hour=20,
        #     minute=52,
        #     id="periodic stock populating",
        #     name="periodic stock populating",
        #     replace_existing=True,
        # )

        scheduler.add_job(
            func=task_populate_trading,
            trigger="interval",
            seconds=10,
            id="populate trading",
            name="populate trading",
            replace_existing=True,
        )

    # xtb_api.get_chart_range_request(end = 1262944412000, period = 1, start = 1262944112000, symbol = 'EURUSD', ticks = 0)

    # import degiroapi
    # from degiroapi.product import Product
    # from degiroapi.order import Order
    # from degiroapi.utils import pretty_json

    # degiro = degiroapi.DeGiro()
    # degiro.login("kimbo91", "SifdjObmnk1")
    # daxsymbols = []
    # products = degiro.get_stock_list(6, 906)
    # for product in products:
    #     daxsymbols.append(Product(product).symbol)
    # degiro.logout()
    # from .models import Broker

    # brokers = ['alpaca', 'binance', 'xtb']

    # for broker in brokers:
    #     new_broker = Broker(name=broker)
    #     db.session.add(new_broker)
    #     db.session.commit()
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
        populate_database()

def populate_database():
    from .database import database

    database.populate_strategies()
    database.populate_filters()
    database.populate_brokers()
    database.populate_alpaca_market()
    database.populate_trading()
    database.populate_user()
    database.populate_xtb_symbols_and_market()
    database.populate_xtb_symbol_prices()
    database.populate_alpaca_symbols()
    database.populate_alpaca_symbol_prices()
    database.populate_binance_symbols()
    database.populate_binance_symbol_prices()

    print("Populated Database!")
    