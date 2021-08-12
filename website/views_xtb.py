from website.models import Param_stock_strategy_breakdown
from flask import Blueprint, render_template, request, redirect, url_for

from flask_login import login_required, current_user

from .extensions import db

from sqlalchemy import desc, asc, func, and_

broker_name = 'xtb'

views_xtb = Blueprint('views_xtb', __name__)


@views_xtb.route('/index/<trading>', methods=['GET', 'POST'])
@login_required
def index(trading):
    # read data from request
    stock_filter = request.args.get('filter')
    rsi_ob = request.args.get('rsi_ob')
    rsi_os = request.args.get('rsi_os')

    from .models import Symbol_XTB_price, Trading, Symbol_XTB, Filter, Broker

    trading = db.session.query(
        Trading
    ).filter(
        Trading.trading == trading
    ).first()

    max_date = (
        db.session
        .query(func.max(Symbol_XTB_price.date))
        .join(Symbol_XTB,Symbol_XTB.id == Symbol_XTB_price.symbol_id)  # or any other `.join(Table2)` would do
        .filter(Symbol_XTB.trading_id == trading.id)
    ).first()[0]

    stocks = []


    # grab latest stock-data according filter
    if stock_filter == 'new_closing_highs':

        from .models import Symbol_XTB, Symbol_XTB_price

        last_orders = db.session.query(
            Symbol_XTB_price.symbol_id, db.func.max(Symbol_XTB_price.close).label('max_close_symbol')
        ).group_by(Symbol_XTB_price.symbol_id).subquery()

        stocks = db.session.query(
                Symbol_XTB_price
            ).join(
                Symbol_XTB, 
                Symbol_XTB.id == Symbol_XTB_price.symbol_id
            ).join(
                last_orders,
                last_orders.c.symbol_id == Symbol_XTB_price.symbol_id
            ).with_entities(
                Symbol_XTB.description.label('name'), 
                Symbol_XTB.symbol, 
                Symbol_XTB.id, 

                Symbol_XTB_price.date, 
                last_orders.c.max_close_symbol,
                Symbol_XTB_price.close, 
                Symbol_XTB_price.sma_20, 
                Symbol_XTB_price.sma_50, 
                Symbol_XTB_price.rsi_14
            ).filter(
                Symbol_XTB_price.close == last_orders.c.max_close_symbol,
                Symbol_XTB_price.date == max_date,
                Symbol_XTB.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_XTB.symbol
                )
            ).all()


    elif stock_filter == 'new_closing_lows':

        last_orders = db.session.query(
            Symbol_XTB_price.symbol_id, db.func.min(Symbol_XTB_price.close).label('min_close_symbol')
        ).group_by(Symbol_XTB_price.symbol_id).subquery()

        from .models import Symbol_XTB, Symbol_XTB_price

        stocks = db.session.query(
                Symbol_XTB_price
            ).join(
                Symbol_XTB, 
                Symbol_XTB.id == Symbol_XTB_price.symbol_id
            ).join(
                last_orders,
                last_orders.c.symbol_id == Symbol_XTB_price.symbol_id
            ).with_entities(
                Symbol_XTB.description.label('name'), 
                Symbol_XTB.symbol, 
                Symbol_XTB.id, 

                Symbol_XTB_price.date, 
                last_orders.c.min_close_symbol,
                Symbol_XTB_price.close, 
                Symbol_XTB_price.sma_20, 
                Symbol_XTB_price.sma_50, 
                Symbol_XTB_price.rsi_14
            ).filter(
                Symbol_XTB_price.close == last_orders.c.min_close_symbol,
                Symbol_XTB_price.date == max_date,
                Symbol_XTB.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_XTB.symbol
                )
            ).all()

    elif stock_filter == 'rsi_overbought':

        from .models import Symbol_XTB, Symbol_XTB_price
        stocks = db.session.query(
                Symbol_XTB_price
            ).join(
                Symbol_XTB, 
                Symbol_XTB_price.symbol_id == Symbol_XTB.id
            ).with_entities(
                Symbol_XTB.description.label('name'), 
                Symbol_XTB.symbol, 
                Symbol_XTB.id, 

                Symbol_XTB_price.date, 
                Symbol_XTB_price.close, 
                Symbol_XTB_price.sma_20, 
                Symbol_XTB_price.sma_50, 
                Symbol_XTB_price.rsi_14
            ).filter(
                Symbol_XTB_price.rsi_14 > str(rsi_ob),
                Symbol_XTB_price.date == max_date,
                Symbol_XTB.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_XTB.symbol
                )
            ).all()

    elif stock_filter == 'rsi_oversold':
        from .models import Symbol_XTB, Symbol_XTB_price
        stocks = db.session.query(
                Symbol_XTB_price
            ).join(
                Symbol_XTB, 
                Symbol_XTB_price.symbol_id == Symbol_XTB.id
            ).with_entities(
                Symbol_XTB.description.label('name'), 
                Symbol_XTB.symbol, 
                Symbol_XTB.id, 

                Symbol_XTB_price.date, 
                Symbol_XTB_price.close, 
                Symbol_XTB_price.sma_20, 
                Symbol_XTB_price.sma_50, 
                Symbol_XTB_price.rsi_14
            ).filter(
                Symbol_XTB_price.rsi_14 < str(rsi_os),
                Symbol_XTB_price.date == max_date,
                Symbol_XTB.trading_id == trading.id
            ).order_by(
                asc(
                    Symbol_XTB.symbol
                )
            ).all()

    else:
        stocks = db.session.query(
                Symbol_XTB
            ).join(
                Symbol_XTB_price, 
                Symbol_XTB_price.symbol_id == Symbol_XTB.id
            ).with_entities(
                Symbol_XTB.description.label('name'), 
                Symbol_XTB.symbol, 
                Symbol_XTB.id, 

                Symbol_XTB_price.date, 
                Symbol_XTB_price.close, 
                Symbol_XTB_price.sma_20, 
                Symbol_XTB_price.sma_50, 
                Symbol_XTB_price.rsi_14
            ).filter(
                Symbol_XTB_price.date == max_date,
                Symbol_XTB.trading_id == trading.id
            ).order_by(
                asc(Symbol_XTB.symbol)
            ).all()

    filters = Filter.query.all()

    broker = db.session.query(
            Broker
        ).filter(
            Broker.name == broker_name
        ).first()

    return render_template(
        "index.html",
        request=request,
        trading = trading,
        broker = broker,
        symbols=stocks,
        user=current_user,
        filters=filters
    )


@views_xtb.route("/symbol/<symbol>", methods=['GET', 'POST'])
@login_required
def stock_detail(symbol):
    # # init database
    # [cursor, connection] = helpers.init_database()
    from .models import Symbol_XTB, Week, Strategy, Strategy_symbol, Symbol_XTB_price, Trading, Broker

    stock = db.session.query(
            Symbol_XTB
        ).join(
            Week, 
            Week.id == Symbol_XTB.week_id
        ).with_entities(
            Symbol_XTB.description.label('name'), 
            Symbol_XTB.symbol, 
            Symbol_XTB.id, 
            Symbol_XTB.trading_id, 

            Week.name.label('market_name'),
            Week.Monday,
            Week.Monday2,
            Week.Tuseday,
            Week.Tuseday2,
            Week.Wednesday,
            Week.Wednesday2,
            Week.Thursday,
            Week.Thursday2,
            Week.Friday,
            Week.Friday2,
            Week.Saturday,
            Week.Saturday2,
            Week.Sunday,
            Week.Sunday2
        ).filter(
            Symbol_XTB.symbol == symbol,
        ).order_by(
            asc(Symbol_XTB.symbol)
        ).one()

    opening_hours = {}

    import datetime
    day_of_week = datetime.datetime.today().weekday()

    txt1 = ""
    txt2 = ""

    if  day_of_week == 0:
        txt1 = stock.Monday
        txt2 = stock.Monday2

    if  day_of_week == 1:
        txt1 = stock.Tuseday
        txt2 = stock.Tuseday2

    if  day_of_week == 2:
        txt1 = stock.Wednesday
        txt2 = stock.Wednesday2

    if  day_of_week == 3:
        txt1 = stock.Thursday
        txt2 = stock.Thursday2

    if  day_of_week == 4:
        txt1 = stock.Friday
        txt2 = stock.Friday2

    if  day_of_week == 5:
        txt1 = stock.Saturday
        txt2 = stock.Saturday2

    if  day_of_week == 6:
        txt1 = stock.Sunday
        txt2 = stock.Sunday2

    hours = txt1.split("-")
    hours1 = hours[0]
    hours2 = hours[1]
    hoursx = txt2.split("-")
    hours3 = hoursx[0]
    hours4 = hoursx[1]

    if hours3:
        opening_hours["morning_open"] = hours1
        opening_hours["morning_close"] = hours2
        opening_hours["evening_open"] = hours3
        opening_hours["evening_close"] = hours4
    else:
        opening_hours["morning_open"] = hours1
        opening_hours["evening_close"] = hours2

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

        # convert stock-id's in an array and write array in List
        stock_id = []
        for temp_stock_id in temp_stock_ids:
            stock_id.append(temp_stock_id.symbol_id)
        stocks[strategy.name] = stock_id

    bars = db.session.query(
            Symbol_XTB_price
        ).filter(
            Symbol_XTB_price.symbol_id == stock.id
        ).order_by(
            desc(Symbol_XTB_price.date)
        ).all()

    symbol = stock.symbol
    try:
        symbol = symbol[:symbol.index(".")]
    except Exception as e:
        symbol = stock.symbol
        
    from .models import Broker
    broker = db.session.query(
        Broker
    ).filter(
        Broker.name == broker_name
    ).first()

    trading = db.session.query(
        Trading
    ).filter(
        Trading.id == stock.trading_id
    ).first()

    return render_template(
        "trading_detail.html",
        user = current_user,
        opening_hours = opening_hours,
        request = request, 
        trading = trading,
        broker = broker,
        stock = stock, 
        symbol = symbol,
        bars = bars,  # recent data of stock
        strategies = strategies,  # possible strategies which can be applied
        parameters_breakout= parameters['opening_range_breakout'],
        parameters_breakdown= parameters['opening_range_breakdown'],
        parameters_bollinger= parameters['bollinger_bands'],
        stocks_breakout= stocks['opening_range_breakout'],
        stocks_breakdown= stocks['opening_range_breakdown'],
        stocks_bollinger= stocks['bollinger_bands']
        )



@views_xtb.route("/apply_strategy", methods=['GET', 'POST'])
@login_required
def apply_strategy():

    strategy_name = request.form.get('strategy_name')
    symbol_id = request.form.get('symbol_id')
    trading_id = request.form.get('trading_id')
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

    return redirect(url_for('views_xtb.strategy', strategy_name = strategy.name, mode = 'applied', trading_id = trading.id))


@views_xtb.route("/strategy/<strategy_name>/<mode>")
@login_required
def strategy(strategy_name, mode):
    strategy_filter = request.args.get('filter')

    from .models import Strategy, Trading, Broker, Symbol_XTB, Param_stock_strategy_breakdown, Param_stock_strategy_breakout, Param_stock_strategy_bollinger, Strategy_symbol

    strategy = db.session.query(
        Strategy
    ).filter(
        Strategy.name == strategy_name
    ).first()

    filter = ""

    trading = {}

    Parameter = None
    if strategy.params == "param_stock_strategy_breakout":
        Parameter = Param_stock_strategy_breakout

    if strategy.params == "param_stock_strategy_breakdown":
        Parameter = Param_stock_strategy_breakdown

    if strategy.params == "param_stock_strategy_bollinger":
        Parameter = Param_stock_strategy_bollinger
        
    broker = db.session.query(
        Broker
    ).filter(
        Broker.name == broker_name
    ).first()

    if strategy_filter is not "" and strategy_filter is not None:

        trading = db.session.query(
                Trading
            ).filter(
                Trading.name == strategy_filter
            ).first()

        hello = db.session.query(
            Parameter
        ).join(
            Strategy_symbol,
            and_(Strategy_symbol.parameter_id == Parameter.parameter_id, Strategy_symbol.symbol_id == Parameter.trading_id)
        ).join(
            Symbol_XTB,
            Symbol_XTB.id == Strategy_symbol.symbol_id
        ).join(
            Trading,
            Trading.id == Symbol_XTB.trading_id
        ).filter(
            Strategy_symbol.strategy_id == strategy.id,
            Strategy_symbol.broker_id == broker.id,
            Parameter.trading == trading.id
        ).all()
        
        filter = " and " + strategy.params + ".trading = "+ str(trading.id)

    else:
        trading['name'] = "All symbol"

    applied_stocks = db.session.execute("SELECT * from " + strategy.params + "\
        join strategy_symbol on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
        join symbol_xtb on symbol_xtb.id = strategy_symbol.symbol_id\
        join trading on symbol_xtb.trading_id = trading.id\
        where strategy_symbol.strategy_id = " + str(strategy.id) + " and strategy_symbol.broker_id = "+str(broker.id)+filter+"\
        GROUP BY strategy_symbol.parameter_id\
        ORDER BY symbol")


    # hello = db.session.query(
    #     Parameter
    # ).join(
    #     Strategy_symbol,
    #     and_(Strategy_symbol.parameter_id == Parameter.parameter_id, Strategy_symbol.symbol_id == Parameter.trading_id)
    # ).join(
    #     Symbol_XTB,
    #     Symbol_XTB.id == Strategy_symbol.symbol_id
    # ).join(
    #     Trading,
    #     Trading.id == Symbol_XTB.trading_id
    # ).filter(
    #     Strategy_symbol.strategy_id == strategy.id,
    #     Strategy_symbol.broker_id == broker.id
    # ).all()
    # print(f"Hello: {hello}")

    saved_stocks = db.session.execute("SELECT * from " + strategy.params + "\
        join strategy_symbol on " + strategy.params + ".parameter_id = strategy_symbol.parameter_id and " + strategy.params + ".trading_id = strategy_symbol.symbol_id\
        join symbol_xtb on symbol_xtb.id = " + strategy.params + ".trading_id\
        where strategy_symbol.broker_id = "+str(broker.id)+filter+"\
        ORDER BY id")


    list_applied_stocks = []
    list_stocks_applied = []
    list_names_applied = []
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

@views_xtb.route("/strategies", methods = ['GET', 'POST'])
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