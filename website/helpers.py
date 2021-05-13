import math
import pandas as pd
from website import config
import sqlite3  # database
import alpaca_trade_api as tradeapi  # API


def calculate_quantity(size, price):
    quantity = math.floor(size / price)
    return quantity


def get_date_today():
    current_date = pd.Timestamp.today().strftime("%Y-%m-%d")
    return current_date


def get_timestamp(date, time, timezone):
    current_timestamp = pd.Timestamp(f"{date} {time}", tz=timezone)
    return current_timestamp

def get_timestamp2(date_time, timezone):
    current_timestamp = pd.Timestamp(f"{date_time}", tz=timezone)
    return current_timestamp

def login_api_alpaca():
    api = tradeapi.REST(config.API_KEY_ALPACA,
                        config.API_SECRET_ALPACA,
                        base_url=config.API_URL)
    return api


def init_database():
    connection = sqlite3.connect(config.DB_LINK)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return [cursor, connection]


def get_strategy_id(cursor, strategy_name):
    cursor.execute("""
        select id from strategy where name = ?
    """, (strategy_name, ))
    strategy_id = cursor.fetchone()['id']
    return strategy_id

def get_names_from_market(cursor, ):
    cursor.execute("""
        SELECT name FROM market
    """)
    markets = cursor.fetchall()
    return markets

def get_market_id(cursor, market_name):
    cursor.execute("""
        select id from market where exchange = ?
    """, (market_name, ))
    market_id = cursor.fetchone()['id']
    return market_id

def get_name_from_market_id(cursor, market_id):
    # Get Stocks which get handled with opening range breakout strategy
    cursor.execute(
        """
        select name from market where id = ?
    """, (market_id, ))
    market_name = cursor.fetchone()['name']
    return market_name