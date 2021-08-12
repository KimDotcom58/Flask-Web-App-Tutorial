from .extensions import scheduler
from .strategies.opening_breakout import opening_breakout
from .strategies.opening_breakdown import opening_breakdown
from .strategies.bollinger_bands import bollinger_bands

# interval example
def task_populate_database():
    with scheduler.app.app_context():
        from .database import database
        database.populate_alpaca_symbols()
        database.populate_alpaca_symbol_prices()
        database.populate_binance_symbols()
        database.populate_binance_symbol_prices()
        database.populate_xtb_symbols_and_market()
        database.populate_xtb_symbol_prices()
    print('Job \'Populate database\' executed')

def task_populate_trading():
    with scheduler.app.app_context():
        from .database import database
        # database.populate_alpaca_symbols()
        # database.populate_alpaca_symbol_prices()
        # database.populate_binance_symbols()
        # database.populate_binance_symbol_prices()
        # database.populate_xtb_symbols_and_market()
        # database.populate_xtb_symbol_prices()
    print('Job \'trading\' executed')

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


def task2():
    print("running task 2!")
