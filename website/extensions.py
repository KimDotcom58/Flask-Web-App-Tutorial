"""Initialize any app extensions."""

from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from website.helpers import helpers
import website.config as config
from website.XTBApi.api import Client

scheduler = APScheduler()

db = SQLAlchemy()
db_name = 'app.db'
# ... any other stuff.. db, caching, sessions, etc.

alpaca_api = helpers.login_api_alpaca()                                                                    # login to alpaca api

# FIRST INIT THE CLIENT
xtb_api = Client()
xtb_api.login(config.XTB_ID_DEMO, config.XTB_PASSWORD_DEMO, mode='demo')
