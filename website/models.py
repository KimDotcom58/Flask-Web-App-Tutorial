from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

class Market(db.Model):
    __tablename__ = 'market'
    stocks = db.relationship("Stock", back_populates="market")
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    exchange = db.Column(db.Text, unique=True, nullable=False)
    market_open_local = db.Column(db.Text, nullable=False)
    market_close_local = db.Column(db.Text, nullable=False)
    timezone = db.Column(db.Text, nullable=False)
    pause_start = db.Column(db.Text)
    pause_stop = db.Column(db.Text)

class Stock(db.Model):
    __tablename__ = 'stock'
    stock_prices = db.relationship("Stock_price", back_populates="stock")
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    symbol = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('market.id'))
    market = db.relationship('Market', back_populates="stocks")
    shortable = db.Column(db.Boolean, nullable=False)

class Stock_price(db.Model):
    __tablename__ = 'stock_price'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    stock = db.relationship('Stock', back_populates="stock_prices")
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Text, nullable=False)
    high = db.Column(db.Text, nullable=False)
    low = db.Column(db.Text, nullable=False)
    close = db.Column(db.Text, nullable=False)
    volume = db.Column(db.Text, nullable=False)
    sma_20 = db.Column(db.Text)
    sma_50 = db.Column(db.Text)
    rsi_14 = db.Column(db.Text)

class Param_stock_strategy_bollinger(db.Model):
    parameter_id = db.Column(db.Integer, primary_key=True)
    trading_id = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    stddev = db.Column(db.Integer, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)

class Param_stock_strategy_breakout(db.Model):
    parameter_id = db.Column(db.Integer, primary_key=True)
    trading_id = db.Column(db.Integer, nullable=False)
    observe_from = db.Column(db.Text, nullable=False)
    observe_until = db.Column(db.Text, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)

class Param_stock_strategy_breakdown(db.Model):
    parameter_id = db.Column(db.Integer, primary_key=True)
    trading_id = db.Column(db.Integer, nullable=False)
    observe_from = db.Column(db.Text, nullable=False)
    observe_until = db.Column(db.Text, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)

class Stock_price_minute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Text, nullable=False)
    open = db.Column(db.Text, nullable=False)
    high = db.Column(db.Text, nullable=False)
    low = db.Column(db.Text, nullable=False)
    close = db.Column(db.Text, nullable=False)
    volume = db.Column(db.Text, nullable=False)

class Stock_strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, nullable=False)
    strategy_id = db.Column(db.Integer, nullable=False)
    parameter_id = db.Column(db.Integer, nullable=False)

class Strategy(db.Model): 
    id = db.Column(db.Integer, primary_key=True, nullable = True)
    name = db.Column(db.Text, nullable=False)
    params = db.Column(db.Text, nullable=False)
    url_pic = db.Column(db.Text, nullable=False)

class Crypto(db.Model):
    __tablename__ = 'crypto'
    crypto_prices = db.relationship("Crypto_price", back_populates="crypto")
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    symbol = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)

class Crypto_price(db.Model):
    __tablename__ = 'crypto_price'
    id = db.Column(db.Integer, primary_key=True)
    crypto_id = db.Column(db.Integer, db.ForeignKey('crypto.id'))
    crypto = db.relationship('Crypto', back_populates="crypto_prices")
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Text, nullable=False)
    high = db.Column(db.Text, nullable=False)
    low = db.Column(db.Text, nullable=False)
    close = db.Column(db.Text, nullable=False)
    volume = db.Column(db.Text, nullable=False)
    sma_20 = db.Column(db.Text)
    sma_50 = db.Column(db.Text)
    rsi_14 = db.Column(db.Text)
 
class Crypto_strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crypto_id = db.Column(db.Integer, nullable=False)
    strategy_id = db.Column(db.Integer, nullable=False)
    parameter_id = db.Column(db.Integer, nullable=False)

class Param_crypto_strategy_bollinger(db.Model):
    parameter_id = db.Column(db.Integer, primary_key=True)
    crypto_id = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    stddev = db.Column(db.Integer, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)
