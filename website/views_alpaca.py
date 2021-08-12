from re import T
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .extensions import db, alpaca_api
import json
from sqlalchemy import desc, asc, func

broker_name = 'alpaca'

views_alpaca = Blueprint('views_alpaca', __name__)

@views_alpaca.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    stock_filter = request.args.get('filter')
    print(stock_filter)

    # orders = alpaca_api.list_orders(status='all', symbol=['A'])
    orders = alpaca_api.list_orders(status=stock_filter)
    # print(orders)

    filters = ["all", "open", "closed"]

    return render_template(
        "orders.html",
        title = 'Stock',
        broker = broker_name,
        user = current_user,
        request = request,
        orders = orders,
        filters = filters
    )

@views_alpaca.route('/index/<trading>', methods=['GET', 'POST'])
@login_required
def index(trading):
    # read data from request
    stock_filter = request.args.get('filter')
    rsi_ob = request.args.get('rsi_ob')
    rsi_os = request.args.get('rsi_os')

    from .models import Symbol_alpaca_price, Trading
    max_date = db.session.query(func.max(Symbol_alpaca_price.date)).first()[0]

    stocks = []

    trading = db.session.query(
        Trading
    ).filter(
        Trading.trading == trading
    ).first()

    # grab latest stock-data according filter
    if stock_filter == 'new_closing_highs':

        from .models import Symbol_alpaca, Symbol_alpaca_price

        last_orders = db.session.query(
            Symbol_alpaca_price.symbol_id, db.func.max(Symbol_alpaca_price.close).label('max_close_stock')
        ).group_by(Symbol_alpaca_price.symbol_id).subquery()

        stocks = db.session.query(
                Symbol_alpaca_price
            ).join(
                Symbol_alpaca, 
                Symbol_alpaca.id == Symbol_alpaca_price.symbol_id
            ).join(
                last_orders,
                last_orders.c.symbol_id == Symbol_alpaca_price.symbol_id
            ).with_entities(
                Symbol_alpaca.name, 
                Symbol_alpaca.symbol, 
                Symbol_alpaca.id, 

                Symbol_alpaca_price.date, 
                last_orders.c.max_close_stock,
                Symbol_alpaca_price.close, 
                Symbol_alpaca_price.sma_20, 
                Symbol_alpaca_price.sma_50, 
                Symbol_alpaca_price.rsi_14
            ).filter(
                Symbol_alpaca_price.close == last_orders.c.max_close_stock,
                Symbol_alpaca_price.date == max_date,
                Symbol_alpaca.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_alpaca.symbol
                )
            ).all()

    elif stock_filter == 'new_closing_lows':

        last_orders = db.session.query(
            Symbol_alpaca_price.symbol_id, db.func.min(Symbol_alpaca_price.close).label('min_close_stock')
        ).group_by(Symbol_alpaca_price.symbol_id).subquery()

        from .models import Symbol_alpaca, Symbol_alpaca_price

        stocks = db.session.query(
                Symbol_alpaca_price
            ).join(
                Symbol_alpaca, 
                Symbol_alpaca.id == Symbol_alpaca_price.symbol_id
            ).join(
                last_orders,
                last_orders.c.symbol_id == Symbol_alpaca_price.symbol_id
            ).with_entities(
                Symbol_alpaca.name, 
                Symbol_alpaca.symbol, 
                Symbol_alpaca.id, 

                Symbol_alpaca_price.date, 
                last_orders.c.min_close_stock,
                Symbol_alpaca_price.close, 
                Symbol_alpaca_price.sma_20, 
                Symbol_alpaca_price.sma_50, 
                Symbol_alpaca_price.rsi_14
            ).filter(
                Symbol_alpaca_price.close == last_orders.c.min_close_stock,
                Symbol_alpaca_price.date == max_date,
                Symbol_alpaca.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_alpaca.symbol
                )
            ).all()

    elif stock_filter == 'rsi_overbought':

        from .models import Symbol_alpaca, Symbol_alpaca_price
        stocks = db.session.query(
                Symbol_alpaca_price
            ).join(
                Symbol_alpaca, 
                Symbol_alpaca_price.symbol_id == Symbol_alpaca.id
            ).with_entities(
                Symbol_alpaca.name, 
                Symbol_alpaca.symbol, 
                Symbol_alpaca.id, 

                Symbol_alpaca_price.date, 
                Symbol_alpaca_price.close, 
                Symbol_alpaca_price.sma_20, 
                Symbol_alpaca_price.sma_50, 
                Symbol_alpaca_price.rsi_14
            ).filter(
                Symbol_alpaca_price.rsi_14 > str(rsi_ob),
                Symbol_alpaca_price.date == max_date,
                Symbol_alpaca.trading_id == trading.id

            ).order_by(
                asc(
                    Symbol_alpaca.symbol
                )
            ).all()

    elif stock_filter == 'rsi_oversold':
        from .models import Symbol_alpaca, Symbol_alpaca_price
        stocks = db.session.query(
                Symbol_alpaca_price
            ).join(
                Symbol_alpaca, 
                Symbol_alpaca_price.symbol_id == Symbol_alpaca.id
            ).with_entities(
                Symbol_alpaca.name, 
                Symbol_alpaca.symbol, 
                Symbol_alpaca.id, 

                Symbol_alpaca_price.date, 
                Symbol_alpaca_price.close, 
                Symbol_alpaca_price.sma_20, 
                Symbol_alpaca_price.sma_50, 
                Symbol_alpaca_price.rsi_14
            ).filter(
                Symbol_alpaca_price.rsi_14 < str(rsi_os),
                Symbol_alpaca_price.date == max_date,
                Symbol_alpaca.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_alpaca.symbol
                )
            ).all()

    else:
        from .models import Symbol_alpaca, Symbol_alpaca_price

        stocks = db.session.query(
                Symbol_alpaca
            ).join(
                Symbol_alpaca_price, 
                Symbol_alpaca_price.symbol_id == Symbol_alpaca.id
            ).with_entities(
                Symbol_alpaca.name, 
                Symbol_alpaca.symbol, 
                Symbol_alpaca.id, 

                Symbol_alpaca_price.date, 
                Symbol_alpaca_price.close, 
                Symbol_alpaca_price.sma_20, 
                Symbol_alpaca_price.sma_50, 
                Symbol_alpaca_price.rsi_14
            ).filter(
                Symbol_alpaca_price.date == max_date,
                Symbol_alpaca.trading_id == trading.id
            ).order_by(
                asc(Symbol_alpaca.symbol)
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
        trading=trading,
        broker=broker,
        symbols=stocks,
        user=current_user,
        filters=filters
    )

@views_alpaca.route("/symbol/<symbol>", methods=['GET', 'POST'])
@login_required
def stock_detail(symbol):

    # # init database
    # [cursor, connection] = helpers.init_database()
    from .models import Symbol_alpaca, Market, Strategy, Strategy_symbol, Symbol_alpaca_price, Trading, Broker
    stock = db.session.query(
            Symbol_alpaca
        ).join(
            Market, 
            Market.id == Symbol_alpaca.market_id
        ).with_entities(
            Symbol_alpaca.name, 
            Symbol_alpaca.symbol, 
            Symbol_alpaca.id, 
            Symbol_alpaca.trading_id, 

            Market.name.label('market_name'),
            Market.market_close_local,
            Market.market_open_local
        ).filter(
            Symbol_alpaca.symbol == symbol
        ).order_by(
            asc(Symbol_alpaca.symbol)
        ).one()

    opening_hours = {}
    opening_hours["morning_open"] = stock.market_open_local
    opening_hours["evening_close"] = stock.market_close_local

    print(opening_hours)

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
    stocks = {}

    for strategy in strategies:
        temp = db.session.execute("SELECT * from strategy_symbol\
            join " + strategy.params + " on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
            where strategy_symbol.symbol_id = "+str(stock.id)+" and strategy_symbol.strategy_id = "+ str(strategy.id))

        stats = []
        for x in temp:
            stats.append(x)
        parameters[strategy.name] = stats
                            
        temp_stock_ids = db.session.query(
            Strategy_symbol
        ).with_entities(
            Strategy_symbol.symbol_id
        ).filter(
            Strategy_symbol.strategy_id == strategy.id
        ).order_by(
            asc(Strategy_symbol.id)
        ).all()

        print(temp_stock_ids)

        # convert stock-id's in an array and write array in List
        symbol_id = []
        for temp_stock_id in temp_stock_ids:
            symbol_id.append(temp_stock_id.symbol_id)
        stocks[strategy.name] = symbol_id

    bars = db.session.query(
            Symbol_alpaca_price
        ).filter(
            Symbol_alpaca_price.symbol_id == stock.id
        ).order_by(
            desc(Symbol_alpaca_price.date)
        ).all()
        
    print(stock.trading_id)

    trading = db.session.query(
        Trading
    ).filter(
        Trading.id == stock.trading_id
    ).first()

    broker = db.session.query(
        Broker
    ).filter(
        Broker.name == broker_name
    ).first()

    return render_template(
        "trading_detail.html",
        user = current_user,
        opening_hours = opening_hours, 
        request = request, 
        broker = broker,
        trading = trading,
        stock = stock, 
        bars = bars,  # recent data of stock
        strategies = strategies,  # possible strategies which can be applied
        parameters_breakout= parameters['opening_range_breakout'],
        parameters_breakdown= parameters['opening_range_breakdown'],
        parameters_bollinger= parameters['bollinger_bands'],
        stocks_breakout= stocks['opening_range_breakout'],
        stocks_breakdown= stocks['opening_range_breakdown'],
        stocks_bollinger= stocks['bollinger_bands']
        )

@views_alpaca.route("/apply_strategy", methods=['GET', 'POST'])
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
        print(f"Observe Until 222: {observe_until}")
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

    from .models import Broker
    broker = db.session.query(
            Broker
        ).filter(
            Broker.name == broker_name
        ).first()

    # insert stock_strategy into database
    new_stock_strategy = Strategy_symbol(symbol_id = symbol_id, strategy_id = strategy.id, parameter_id = parameter_id, is_traded = True, broker_id = broker.id, trading_id = trading.id)
    db.session.add(new_stock_strategy)
    db.session.commit()

    return redirect(url_for('views_alpaca.strategy', strategy_name = strategy.name, mode = 'applied', trading_id = trading_id))

@views_alpaca.route("/strategies", methods = ['GET', 'POST'])
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

@views_alpaca.route("/strategy/<strategy_name>/<mode>")
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

    applied_stocks = db.session.execute("SELECT * from " + strategy.params + "\
        join strategy_symbol on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
        join symbol_alpaca on symbol_alpaca.id = strategy_symbol.symbol_id\
        join trading on symbol_alpaca.trading_id = trading.id\
        where strategy_symbol.strategy_id = " + str(strategy.id) + " and strategy_symbol.broker_id = "+str(broker.id)+filter+"\
        GROUP BY strategy_symbol.parameter_id\
        ORDER BY symbol")

    saved_stocks = db.session.execute("SELECT * from " + strategy.params + "\
        join strategy_symbol on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
        join symbol_alpaca on symbol_alpaca.id = " + strategy.params + ".trading_id\
        where strategy_symbol.broker_id = "+str(broker.id)+filter+"\
        ORDER BY id")

    list_applied_stocks = []
    list_names_applied = []
    list_stocks_applied = []
    for stock in applied_stocks:
        list_applied_stocks.append(stock.parameter_id) # parameter ids of the stocks
        list_stocks_applied.append(stock) # 

        if stock.trading_id not in list_names_applied:
            list_names_applied.append(stock.trading_id)

    list_saved_stocks = []
    list_stocks_saved = []
    is_traded = {}
    list_names_saved = []

    for stock in saved_stocks:
        list_saved_stocks.append(stock.parameter_id) # parameter ids of the stocks
        list_stocks_saved.append(stock) # 
        if stock.parameter_id in list_applied_stocks:
            is_traded[stock.parameter_id] = True
        else:
            is_traded[stock.parameter_id] = False
        
        if stock.trading_id not in list_names_saved:
            list_names_saved.append(stock.trading_id)

    if mode == 'applied':
        stocks = list_stocks_applied
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
        stocks = list_stocks_saved
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
        symbols = stocks,
        strategy = strategy,
        filters = trading_names,
        mode = mode,
        is_traded = is_traded
    )

@views_alpaca.route("/delete_traded_strategy", methods=['GET', 'POST'])
@login_required
def delete_traded_strategy():

    symbol_id = request.form.get('trading_id')
    strategy_name = request.form.get('strategy_name')
    strategy_id = request.form.get('strategy_id')
    parameter_id = request.form.get('parameter_id')

    from .models import Strategy_symbol

    stock = db.session.query(Strategy_symbol).filter_by(strategy_id = strategy_id, parameter_id = parameter_id, symbol_id = symbol_id)
    stock.delete()
    db.session.commit()

    return redirect(url_for('views_alpaca.strategy', strategy_name = strategy_name, mode = 'applied'))

@views_alpaca.route("/apply_saved_strategies/<strategy_name>", methods=['GET', 'POST'])
@login_required
def apply_saved_strategies(strategy_name):

    from .models import Strategy_symbol
    
    array = request.args.get('parameters_to_apply')
    strategy_id = request.args.get('strategy_id')

    # # parse array:
    array_parsed = json.loads(array)
    print(array_parsed)

    saved_stocks = db.session.query(Strategy_symbol).filter_by(strategy_id = strategy_id).all()

    print(f"Saved Stocks 1: {saved_stocks}")

    applied_parameters_on_strategy = []
    for stock in saved_stocks:
        applied_parameters_on_strategy.append(stock.parameter_id)

    # look to insert
    for parsed in array_parsed:
        symbol_id = array_parsed[parsed]['trading_id']
        parameter_id = parsed
        print(parameter_id)

        try:
            b=applied_parameters_on_strategy.index(int(parameter_id))
        except ValueError:
            new_stock_strategy = Strategy_symbol(symbol_id=symbol_id, strategy_id=strategy_id, parameter_id = parameter_id, is_traded = True)
            db.session.add(new_stock_strategy)
            db.session.commit()

    # look to remove
    for saved in saved_stocks:
        print(f"Hallo: {saved.parameter_id}")
        if str(saved.parameter_id) not in array_parsed:
            print(f"Hallo: ")

            db.session.query(Strategy_symbol).filter_by(strategy_id = saved.strategy_id, parameter_id = saved.parameter_id, symbol_id = saved.symbol_id).update({"is_traded": False})
            db.session.commit()

    return redirect(url_for('views_alpaca.strategy', strategy_name = strategy_name, mode = 'saved'))
