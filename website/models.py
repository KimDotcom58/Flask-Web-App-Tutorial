from .extensions import db
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

class Broker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

class Market(db.Model):
    __tablename__ = 'market'
    stocks = db.relationship("Symbol_alpaca", back_populates="market")
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    exchange = db.Column(db.Text, unique=True, nullable=False)
    market_open_local = db.Column(db.Text, nullable=False)
    market_close_local = db.Column(db.Text, nullable=False)
    timezone = db.Column(db.Text, nullable=False)

class Week(db.Model):
    __tablename__ = 'week'
    symbols = db.relationship("Symbol_XTB", back_populates="week")
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    Monday = db.Column(db.Text, nullable=False)
    Monday2 = db.Column(db.Text, nullable=False)
    Tuseday = db.Column(db.Text, nullable=False)
    Tuseday2 = db.Column(db.Text, nullable=False)
    Wednesday = db.Column(db.Text, nullable=False)
    Wednesday2 = db.Column(db.Text, nullable=False)
    Thursday = db.Column(db.Text, nullable=False)
    Thursday2 = db.Column(db.Text, nullable=False)
    Friday = db.Column(db.Text, nullable=False)
    Friday2 = db.Column(db.Text, nullable=False)
    Saturday = db.Column(db.Text, nullable=False)
    Saturday2 = db.Column(db.Text, nullable=False)
    Sunday = db.Column(db.Text, nullable=False)
    Sunday2 = db.Column(db.Text, nullable=False)

class Strategy(db.Model): 
    id = db.Column(db.Integer, primary_key=True, nullable = True)
    name = db.Column(db.Text, nullable=False)
    params = db.Column(db.Text, nullable=False)
    url_pic = db.Column(db.Text, nullable=False)
    
class Param_stock_strategy_bollinger(db.Model):
    parameter_id = db.Column(db.Integer, primary_key=True)
    trading_id = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    stddev = db.Column(db.Integer, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)
    trading = db.Column(db.Integer, nullable=False)

class Param_stock_strategy_breakout(db.Model):
    parameter_id = db.Column(db.Integer, primary_key=True)
    trading_id = db.Column(db.Integer, nullable=False)
    observe_from = db.Column(db.Text, nullable=False)
    observe_until = db.Column(db.Text, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)
    trading = db.Column(db.Integer, nullable=False)

class Param_stock_strategy_breakdown(db.Model):
    parameter_id = db.Column(db.Integer, primary_key=True)
    trading_id = db.Column(db.Integer, nullable=False)
    observe_from = db.Column(db.Text, nullable=False)
    observe_until = db.Column(db.Text, nullable=False)
    trade_price = db.Column(db.Integer, nullable=False)
    trading = db.Column(db.Integer, nullable=False)

class Trading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trading = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False, unique=True)

class Symbol_alpaca(db.Model):
    __tablename__ = 'symbol_alpaca'
    symbol_prices = db.relationship("Symbol_alpaca_price", back_populates="symbol")
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    trading_id = db.Column(db.Integer, nullable=True)
    symbol = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('market.id'))
    market = db.relationship('Market', back_populates="stocks")
    shortable = db.Column(db.Boolean, nullable=False)

class Symbol_binance(db.Model):
    __tablename__ = 'symbol_binance'
    symbol_prices = db.relationship("Symbol_binance_price", back_populates="symbol")
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    symbol = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    trading_id = db.Column(db.Integer, nullable = False)


class Symbol_XTB(db.Model):
    __tablename__ = 'symbol_XTB'
    symbol_prices = db.relationship("Symbol_XTB_price", back_populates="symbol")
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    symbol = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    trading_id = db.Column(db.Integer, nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'))
    week = db.relationship('Week', back_populates="symbols")
    currency = db.Column(db.Text, nullable=False)
    trailing_enabled = db.Column(db.Boolean, nullable=False)


class Symbol_alpaca_price(db.Model):
    __tablename__ = 'symbol_alpaca_price'
    id = db.Column(db.Integer, primary_key=True)
    symbol_id = db.Column(db.Integer, db.ForeignKey('symbol_alpaca.id'))
    symbol = db.relationship('Symbol_alpaca', back_populates="symbol_prices")
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Text, nullable=False)
    high = db.Column(db.Text, nullable=False)
    low = db.Column(db.Text, nullable=False)
    close = db.Column(db.Text, nullable=False)
    volume = db.Column(db.Text, nullable=False)
    sma_20 = db.Column(db.Text)
    sma_50 = db.Column(db.Text)
    rsi_14 = db.Column(db.Text)


class Symbol_binance_price(db.Model):
    __tablename__ = 'symbol_binance_price'
    id = db.Column(db.Integer, primary_key=True)
    symbol_id = db.Column(db.Integer, db.ForeignKey('symbol_binance.id'))
    symbol = db.relationship('Symbol_binance', back_populates="symbol_prices")
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Text, nullable=False)
    high = db.Column(db.Text, nullable=False)
    low = db.Column(db.Text, nullable=False)
    close = db.Column(db.Text, nullable=False)
    volume = db.Column(db.Text, nullable=False)
    sma_20 = db.Column(db.Text)
    sma_50 = db.Column(db.Text)
    rsi_14 = db.Column(db.Text)
 

class Symbol_XTB_price(db.Model):
    __tablename__ = 'symbol_XTB_price'
    id = db.Column(db.Integer, primary_key=True)
    symbol_id = db.Column(db.Integer, db.ForeignKey('symbol_XTB.id'))
    symbol = db.relationship('Symbol_XTB', back_populates="symbol_prices")
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Text, nullable=False)
    high = db.Column(db.Text, nullable=False)
    low = db.Column(db.Text, nullable=False)
    close = db.Column(db.Text, nullable=False)
    volume = db.Column(db.Text, nullable=False)
    sma_20 = db.Column(db.Text)
    sma_50 = db.Column(db.Text)
    rsi_14 = db.Column(db.Text)

class Stock_price_minute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Text, nullable=False)
    open = db.Column(db.Text, nullable=False)
    high = db.Column(db.Text, nullable=False)
    low = db.Column(db.Text, nullable=False)
    close = db.Column(db.Text, nullable=False)
    volume = db.Column(db.Text, nullable=False)

class Strategy_symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol_id = db.Column(db.Integer, nullable=False)
    strategy_id = db.Column(db.Integer, nullable=False)
    parameter_id = db.Column(db.Integer, nullable=False)
    broker_id = db.Column(db.Integer, nullable=False)
    trading_id = db.Column(db.Integer, nullable=False)
    is_traded = db.Column(db.Boolean, nullable=False)

