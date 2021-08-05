from .extensions import scheduler
from .strategies.opening_breakout import opening_breakout
from .strategies.opening_breakdown import opening_breakdown
from .strategies.bollinger_bands import bollinger_bands

# interval example
def task_populate_database():
    with scheduler.app.app_context():
        from .database import database
        database.populate_alpaca_stocks()
        database.populate_alpaca_stock_prices()
    print('Job \'Populate database\' executed')

def task_populate_trading():
    with scheduler.app.app_context():
        from .database import database
        database.test_XY()
    print('Job 2 executed')

def task_strategy_opening_breakout():
    with scheduler.app.app_context():
        opening_breakout.strategy()
    print('Job \'breakout\' executed')

def task_strategy_opening_breakdown():
    with scheduler.app.app_context():
        opening_breakdown.strategy()
    print('Job \'breakdown\' executed')

def task_strategy_bollinger():
    with scheduler.app.app_context():
        bollinger_bands.strategy()
    print('Job \'bollinger\' executed')

# def task_backtest():
#     with scheduler.app.app_context():
#         bt.OpeningRangeBreakout()
#     print('Job bollinger XXXXX executed')

def task2():
    print("running task 2!")
