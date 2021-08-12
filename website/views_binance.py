from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .extensions import db, alpaca_api
import json
from sqlalchemy import desc, asc, func
broker_name = 'binance'
views_binance = Blueprint('views_binance', __name__)

@views_binance.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():

    orders = alpaca_api.list_orders(status='all')

    print(orders)
    
    return render_template(
        "orders.html",
        title = 'Crypto',
        broker = 'binance',
        user = current_user,
        request = request,
        orders = orders
    )

@views_binance.route('/index/<trading>', methods=['GET', 'POST'])
@login_required
def index(trading):
    # read data from request7
    print(trading)
    crypto_filter = request.args.get('filter')
    rsi_ob = request.args.get('rsi_ob')
    rsi_os = request.args.get('rsi_os')

    from .models import Symbol_binance_price, Trading, Symbol_binance
    # max_date = db.session.query(func.max(Symbol_binance_price.date)).first()[0]


    trading = db.session.query(
        Trading
    ).filter(
        Trading.trading == trading
    ).first()


    max_date = (
        db.session
        .query(func.max(Symbol_binance_price.date))
        .join(Symbol_binance,Symbol_binance.id == Symbol_binance_price.symbol_id)  # or any other `.join(Table2)` would do
        .filter(Symbol_binance.trading_id == trading.id)
    ).first()[0]

    # grab latest stock-data according filter
    if crypto_filter == 'new_closing_highs':

        from .models import Symbol_binance, Symbol_binance_price

        last_orders = db.session.query(
            Symbol_binance_price.symbol_id, db.func.max(Symbol_binance_price.close).label('max_close_Crypto')
        ).group_by(Symbol_binance_price.symbol_id).subquery()

        Cryptos = db.session.query(
                Symbol_binance_price
            ).join(
                Symbol_binance, 
                Symbol_binance.id == Symbol_binance_price.symbol_id
            ).join(
                last_orders,
                last_orders.c.symbol_id == Symbol_binance_price.symbol_id
            ).with_entities(
                Symbol_binance.name, 
                Symbol_binance.symbol, 
                Symbol_binance.id, 

                Symbol_binance_price.date, 
                last_orders.c.max_close_Crypto,
                Symbol_binance_price.close, 
                Symbol_binance_price.sma_20, 
                Symbol_binance_price.sma_50, 
                Symbol_binance_price.rsi_14
            ).filter(
                Symbol_binance_price.close == last_orders.c.max_close_Crypto,
                Symbol_binance_price.date == max_date,
                Symbol_binance.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_binance.symbol
                )
            ).all()

    elif crypto_filter == 'new_closing_lows':

        last_orders = db.session.query(
            Symbol_binance_price.symbol_id, db.func.min(Symbol_binance_price.close).label('min_close_Crypto')
        ).group_by(Symbol_binance_price.symbol_id).subquery()

        from .models import Symbol_binance, Symbol_binance_price

        Cryptos = db.session.query(
                Symbol_binance_price
            ).join(
                Symbol_binance, 
                Symbol_binance.id == Symbol_binance_price.symbol_id
            ).join(
                last_orders,
                last_orders.c.symbol_id == Symbol_binance_price.symbol_id
            ).with_entities(
                Symbol_binance.name, 
                Symbol_binance.symbol, 
                Symbol_binance.id, 

                Symbol_binance_price.date, 
                last_orders.c.min_close_Crypto,
                Symbol_binance_price.close, 
                Symbol_binance_price.sma_20, 
                Symbol_binance_price.sma_50, 
                Symbol_binance_price.rsi_14
            ).filter(
                Symbol_binance_price.close == last_orders.c.min_close_Crypto,
                Symbol_binance_price.date == max_date,
                Symbol_binance.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_binance.symbol
                )
            ).all()

    elif crypto_filter == 'rsi_overbought':

        from .models import Symbol_binance, Symbol_binance_price
        Cryptos = db.session.query(
                Symbol_binance_price
            ).join(
                Symbol_binance, 
                Symbol_binance_price.symbol_id == Symbol_binance.id
            ).with_entities(
                Symbol_binance.name, 
                Symbol_binance.symbol, 
                Symbol_binance.id, 

                Symbol_binance_price.date, 
                Symbol_binance_price.close, 
                Symbol_binance_price.sma_20, 
                Symbol_binance_price.sma_50, 
                Symbol_binance_price.rsi_14
            ).filter(
                Symbol_binance_price.rsi_14 > str(rsi_ob),
                Symbol_binance_price.date == max_date,
                Symbol_binance.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_binance.symbol
                )
            ).all()

    elif crypto_filter == 'rsi_oversold':
        from .models import Symbol_binance, Symbol_binance_price
        Cryptos = db.session.query(
                Symbol_binance_price
            ).join(
                Symbol_binance, 
                Symbol_binance_price.symbol_id == Symbol_binance.id
            ).with_entities(
                Symbol_binance.name, 
                Symbol_binance.symbol, 
                Symbol_binance.id, 

                Symbol_binance_price.date, 
                Symbol_binance_price.close, 
                Symbol_binance_price.sma_20, 
                Symbol_binance_price.sma_50, 
                Symbol_binance_price.rsi_14
            ).filter(
                Symbol_binance_price.rsi_14 < str(rsi_os),
                Symbol_binance_price.date == max_date,
                Symbol_binance.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_binance.symbol
                )
            ).all()

    else:
        from .models import Symbol_binance, Symbol_binance_price

        Cryptos = db.session.query(
                Symbol_binance
            ).join(
                Symbol_binance_price, 
                Symbol_binance_price.symbol_id == Symbol_binance.id
            ).with_entities(
                Symbol_binance.name, 
                Symbol_binance.symbol, 
                Symbol_binance.id, 

                Symbol_binance_price.date, 
                Symbol_binance_price.close, 
                Symbol_binance_price.sma_20, 
                Symbol_binance_price.sma_50, 
                Symbol_binance_price.rsi_14
            ).filter(
                Symbol_binance_price.date == max_date,
                Symbol_binance.trading_id == trading.id
            ).order_by(
                asc(Symbol_binance.symbol)
            ).all()

    from .models import Filter
    filters = Filter.query.all()

    from .models import Broker
    broker = db.session.query(
            Broker
        ).filter(
            Broker.name == broker_name
        ).first()

    return render_template(
        "index.html",
        request=request,
        broker = broker,
        trading=trading,
        symbols=Cryptos,
        user=current_user,
        filters=filters
    )

@views_binance.route("/symbol/<symbol>", methods=['GET', 'POST'])
@login_required
def crypto_detail(symbol):

    print(symbol)

    # # init database
    # [cursor, connection] = helpers.init_database()
    from .models import Symbol_binance, Strategy, Strategy_symbol, Symbol_binance_price, Trading, Broker
    crypto = db.session.query(
            Symbol_binance
        ).with_entities(
            Symbol_binance.name, 
            Symbol_binance.symbol, 
            Symbol_binance.id, 
            Symbol_binance.trading_id, 
        ).filter(
            Symbol_binance.symbol == symbol
        ).order_by(
            asc(Symbol_binance.symbol)
        ).one()

    strategies = db.session.query(
            Strategy
        ).with_entities(
            Strategy.name, 
            Strategy.id, 
            Strategy.params
        ).order_by(
            asc(Strategy.id)
        ).all()

    # loop through the strategies and create:
    #   - List SQL:         active parameters on stock
    #   - List Array:       active stock-id's on strategy
    #   - List SQL:

    # List {'strategy-name':[strategy-parameters of stock-specific]}
    parameters = {}

    # List {'strategy-name':[strategy-id's (actively) applied]}
    cryptos = {}

    for strategy in strategies:
        temp = db.session.execute("SELECT * from strategy_symbol\
            join " + strategy.params + " on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
            where strategy_symbol.symbol_id = "+str(crypto.id)+" and strategy_symbol.strategy_id = "+ str(strategy.id))

        stats = []
        for x in temp:
            stats.append(x)
        parameters[strategy.name] = stats
                            
        temp_crypto_ids = db.session.query(
            Strategy_symbol
        ).with_entities(
            Strategy_symbol.symbol_id
        ).filter(
            Strategy_symbol.strategy_id == strategy.id
        ).order_by(
            asc(Strategy_symbol.id)
        ).all()

        # convert stock-id's in an array and write array in List
        symbol_id = []
        for temp_crypto_id in temp_crypto_ids:
            symbol_id.append(temp_crypto_id.symbol_id)
        cryptos[strategy.name] = symbol_id

    bars = db.session.query(
            Symbol_binance_price
        ).filter(
            Symbol_binance_price.symbol_id == crypto.id
        ).order_by(
            desc(Symbol_binance_price.date)
        ).all()
        
    trading = db.session.query(
        Trading
    ).filter(
        Trading.id == crypto.trading_id
    ).first()

    broker = db.session.query(
        Broker
    ).filter(
        Broker.name == broker_name
    ).first()




    return render_template(
        "trading_detail.html",
        user = current_user,
        request = request, 
        broker = broker,
        trading = trading,
        stock = crypto, 
        bars = bars,  # recent data of stock
        strategies = strategies,  # possible strategies which can be applied
        parameters_bollinger= parameters['bollinger_bands'],
        stocks_bollinger= cryptos['bollinger_bands']
        )

@views_binance.route("/apply_strategy", methods=['GET', 'POST'])
@login_required
def apply_strategy():

    strategy_name = request.form.get('strategy_name')
    symbol_id = request.form.get('symbol_id')
    trading_id = request.form.get('trading_id')
    print(f"symbol_id: {symbol_id}")
    print(f"trading_id: {trading_id}")
    trade_price = request.form.get('trade_price')
    observe_from = request.form.get('observe_from')
    observe_until = request.form.get('observe_until')
    period = request.form.get('period')
    stddev = request.form.get('stddev')

    from .models import Strategy, Strategy_symbol, Trading, Param_stock_strategy_breakdown, Param_stock_strategy_breakout, Param_stock_strategy_bollinger

    strategy = db.session.query(
            Strategy
        ).with_entities(
            Strategy.id,
            Strategy.params,
            Strategy.name
        ).filter(
            Strategy.name == strategy_name
        ).first()

    trading = db.session.query(
        Trading
    ).filter(
        Trading.id == trading_id
    ).first()

    # insert parameters into database

    if strategy.params == "param_stock_strategy_breakdown":

        new_param_breakdown = Param_stock_strategy_breakdown(trading_id = symbol_id, observe_from = observe_from, observe_until = observe_until, trade_price = trade_price, trading = trading.id)
        db.session.add(new_param_breakdown)
        db.session.commit()
    
    elif strategy.params == "param_stock_strategy_breakout":

        new_param_breakout = Param_stock_strategy_breakout(trading_id = symbol_id, observe_from = observe_from, observe_until = observe_until, trade_price = trade_price, trading = trading.id)
        db.session.add(new_param_breakout)
        db.session.commit()

    elif strategy.params == "param_stock_strategy_bollinger":

        new_param_bollinger = Param_stock_strategy_bollinger(trading_id = symbol_id, period = period, stddev = stddev, trade_price = trade_price, trading = trading.id)
        db.session.add(new_param_bollinger)
        db.session.commit()
    try:
        parameter_id = db.session.execute("select * from " + strategy.params + " where parameter_id = (select max(parameter_id) from " + strategy.params + ")").first().parameter_id
    except Exception as e:
        parameter_id = 0

    # insert stock_strategy into database
    new_stock_strategy = Strategy_symbol(symbol_id = symbol_id, strategy_id = strategy.id, parameter_id = parameter_id, is_traded = True)
    db.session.add(new_stock_strategy)
    db.session.commit()

    return redirect(url_for('views_binance.strategy', strategy_name = strategy.name, mode = 'applied'))

@views_binance.route("/strategies", methods = ['GET', 'POST'])
@login_required
def strategies():

    from .models import Strategy, Trading, Broker

    strategies = db.session.query(
            Strategy
        ).with_entities(
            Strategy.name, 
            Strategy.id, 
            Strategy.params,
            Strategy.url_pic
        ).order_by(
            asc(Strategy.id)
        ).all()

    trading = db.session.query(
        Trading
    ).all()

    broker = db.session.query(
        Broker
    ).filter(
        Broker.name == broker_name
    ).first()

    return render_template(
        "strategies.html",
        broker = broker,
        trading = trading, 
        user = current_user,
        request = request,
        strategies = strategies
    )

@views_binance.route("/strategy/<strategy_name>/<mode>")
@login_required
def strategy(strategy_name, mode):
    strategy_filter = request.args.get('filter')
    print(strategy_filter)
    from .models import Strategy, Trading, Broker

    strategy = db.session.query(
        Strategy
    ).filter(
        Strategy.name == strategy_name
    ).first()

    filter = ""

    trading = {}
        
    if strategy_filter is not "" and strategy_filter is not None:

        trading = db.session.query(
                Trading
            ).filter(
                Trading.name == strategy_filter
            ).first()

        filter = " and " + strategy.params + ".trading = "+ str(trading.id)

    else:
        trading['name'] = "All symbol"

    broker = db.session.query(
        Broker
    ).filter(
        Broker.name == broker_name
    ).first()

    applied_cryptos = db.session.execute("SELECT * from " + strategy.params + "\
        join strategy_symbol on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
        join symbol_binance on symbol_binance.id = strategy_symbol.symbol_id\
        join trading on symbol_xtb.trading_id = trading.id\
        where strategy_symbol.strategy_id = " + str(strategy.id) + " and strategy_symbol.broker_id = "+str(broker.id)+filter+"\
        GROUP BY strategy_symbol.parameter_id\
        ORDER BY symbol")

    saved_cryptos = db.session.execute("SELECT * from " + strategy.params + "\
        join strategy_symbol on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
        join symbol_binance on symbol_binance.id = " + strategy.params + ".trading_id\
        where strategy_symbol.broker_id = "+str(broker.id)+filter+"\
        ORDER BY id")

    list_applied_cryptos = []
    list_names_applied = []
    list_cryptos_applied = []
    for crypto in applied_cryptos:
        list_applied_cryptos.append(crypto.parameter_id) # parameter ids of the stocks
        list_cryptos_applied.append(crypto) # 

        if crypto.trading_id not in list_names_applied:
            list_names_applied.append(crypto.trading_id)

    list_saved_cryptos = []
    list_cryptos_saved = []
    is_traded = {}
    list_names_saved = []


    for crypto in saved_cryptos:
        list_saved_cryptos.append(crypto.parameter_id) # parameter ids of the stocks
        list_cryptos_saved.append(crypto) # 
        if crypto.parameter_id in list_applied_cryptos:
            is_traded[crypto.parameter_id] = True
        else:
            is_traded[crypto.parameter_id] = False
        print(f"saved: {crypto}")
        
        if crypto.trading_id not in list_names_saved:
            list_names_saved.append(crypto.trading_id)

    if mode == 'applied':
        cryptos = list_cryptos_applied
        names = []
        for name in list_names_applied:
            print(name)
            names.append(
                db.session.query(
                    Trading
                ).filter(
                    Trading.id == name
                ).first()
            )
        print(names)

    if mode == 'saved':
        cryptos = list_cryptos_saved
        names = []
        for name in list_names_applied:
            print(name)
            names.append(
                db.session.query(
                    Trading
                ).filter(
                    Trading.id == name
                ).first()
            )
        print(names)

    trading_names = [name.name for name in names]


    return render_template(
        "strategy.html",
        broker = broker,
        trading = trading,
        user = current_user,
        request = request,
        symbols = cryptos,
        strategy = strategy,
        filters = trading_names,
        mode = mode,
        is_traded = is_traded
    )

@views_binance.route("/delete_traded_strategy", methods=['GET', 'POST'])
@login_required
def delete_traded_strategy():

    symbol_id = request.form.get('trading_id')
    strategy_name = request.form.get('strategy_name')
    strategy_id = request.form.get('strategy_id')
    parameter_id = request.form.get('parameter_id')

    from .models import Strategy_symbol

    crypto = db.session.query(Strategy_symbol).filter_by(strategy_id = strategy_id, parameter_id = parameter_id, symbol_id = symbol_id)
    crypto.delete()
    db.session.commit()

    return redirect(url_for('views_binance.strategy', strategy_name = strategy_name, mode = 'applied'))


@views_binance.route("/apply_saved_strategies/<strategy_name>", methods=['GET', 'POST'])
@login_required
def apply_traded_strategy(strategy_name):

    from .models import Strategy_symbol

    array = request.args.get('parameters_to_apply')
    strategy_id = request.args.get('strategy_id')

    # # parse array:
    array_parsed = json.loads(array)
    print(f"array_parsed: {array_parsed}")

    saved_cryptos = db.session.query(Strategy_symbol).filter_by(strategy_id = strategy_id).all()

    print(f"Saved Cryptos 1: {saved_cryptos}")

    applied_parameters_on_strategy = []
    for crypto in saved_cryptos:
        applied_parameters_on_strategy.append(crypto.parameter_id)

    # look to insert
    for parsed in array_parsed:
        symbol_id = array_parsed[parsed]['trading_id']
        parameter_id = parsed
        print(parameter_id)

        try:
            b=applied_parameters_on_strategy.index(int(parameter_id))
        except ValueError:
            new_crypto_strategy = Strategy_symbol(symbol_id=symbol_id, strategy_id=strategy_id, parameter_id = parameter_id, is_traded = True)
            db.session.add(new_crypto_strategy)
            db.session.commit()

    # look to remove
    for saved in saved_cryptos:
        if str(saved.parameter_id) not in array_parsed:
            print(f"Hallo: ")
            crypto = db.session.query(Strategy_symbol).filter_by(strategy_id = saved.strategy_id, parameter_id = saved.parameter_id, symbol_id = saved.symbol_id)
            crypto.delete()
            db.session.commit()

    return redirect(url_for('views_binance.strategy', strategy_name = strategy_name, mode = 'saved'))
