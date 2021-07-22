from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from .extensions import db_name

"""App configuration."""


class Config:
    """Prod config."""

    DEBUG = False
    TESTING = False
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url="sqlite:///website/"+db_name)
    }

class DevelopmentConfig(Config):
    """Dev config."""

    DEBUG = True
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url="sqlite:///website/"+db_name)
    }