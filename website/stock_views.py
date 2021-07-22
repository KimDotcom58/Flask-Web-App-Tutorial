from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .extensions import db, alpaca_api
import json
from sqlalchemy import desc, asc, func

stock_views = Blueprint('stock_views', __name__)

@stock_views.route('/orders', methods=['GET', 'POST'])
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
        user = current_user,
        request = request,
        orders = orders,
        filters = filters
    )

@stock_views.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # read data from request
    stock_filter = request.args.get('filter')
    rsi_ob = request.args.get('rsi_ob')
    rsi_os = request.args.get('rsi_os')

    from .models import Stock_price
    max_date = db.session.query(func.max(Stock_price.date)).first()[0]

    stocks = []

    # grab latest stock-data according filter
    if stock_filter == 'new_closing_highs':

        from .models import Stock, Stock_price

        last_orders = db.session.query(
            Stock_price.stock_id, db.func.max(Stock_price.close).label('max_close_stock')
        ).group_by(Stock_price.stock_id).subquery()

        stocks = db.session.query(
                Stock_price
            ).join(
                Stock, 
                Stock.id == Stock_price.stock_id
            ).join(
                last_orders,
                last_orders.c.stock_id == Stock_price.stock_id
            ).with_entities(
                Stock.name, 
                Stock.symbol, 
                Stock.id, 

                Stock_price.date, 
                last_orders.c.max_close_stock,
                Stock_price.close, 
                Stock_price.sma_20, 
                Stock_price.sma_50, 
                Stock_price.rsi_14
            ).filter(
                Stock_price.close == last_orders.c.max_close_stock,
                Stock_price.date == max_date
            ).order_by(
                asc(
                    Stock.symbol
                )
            ).all()

    elif stock_filter == 'new_closing_lows':

        last_orders = db.session.query(
            Stock_price.stock_id, db.func.min(Stock_price.close).label('min_close_stock')
        ).group_by(Stock_price.stock_id).subquery()

        from .models import Stock, Stock_price

        stocks = db.session.query(
                Stock_price
            ).join(
                Stock, 
                Stock.id == Stock_price.stock_id
            ).join(
                last_orders,
                last_orders.c.stock_id == Stock_price.stock_id
            ).with_entities(
                Stock.name, 
                Stock.symbol, 
                Stock.id, 

                Stock_price.date, 
                last_orders.c.min_close_stock,
                Stock_price.close, 
                Stock_price.sma_20, 
                Stock_price.sma_50, 
                Stock_price.rsi_14
            ).filter(
                Stock_price.close == last_orders.c.min_close_stock,
                Stock_price.date == max_date
            ).order_by(
                asc(
                    Stock.symbol
                )
            ).all()

    elif stock_filter == 'rsi_overbought':

        from .models import Stock, Stock_price
        stocks = db.session.query(
                Stock_price
            ).join(
                Stock, 
                Stock_price.stock_id == Stock.id
            ).with_entities(
                Stock.name, 
                Stock.symbol, 
                Stock.id, 

                Stock_price.date, 
                Stock_price.close, 
                Stock_price.sma_20, 
                Stock_price.sma_50, 
                Stock_price.rsi_14
            ).filter(
                Stock_price.rsi_14 > str(rsi_ob),
                Stock_price.date == max_date
            ).order_by(
                asc(
                    Stock.symbol
                )
            ).all()

    elif stock_filter == 'rsi_oversold':
        from .models import Stock, Stock_price
        stocks = db.session.query(
                Stock_price
            ).join(
                Stock, 
                Stock_price.stock_id == Stock.id
            ).with_entities(
                Stock.name, 
                Stock.symbol, 
                Stock.id, 

                Stock_price.date, 
                Stock_price.close, 
                Stock_price.sma_20, 
                Stock_price.sma_50, 
                Stock_price.rsi_14
            ).filter(
                Stock_price.rsi_14 < str(rsi_os),
                Stock_price.date == max_date
            ).order_by(
                asc(
                    Stock.symbol
                )
            ).all()

    else:
        from .models import Stock, Stock_price

        stocks = db.session.query(
                Stock
            ).join(
                Stock_price, 
                Stock_price.stock_id == Stock.id
            ).with_entities(
                Stock.name, 
                Stock.symbol, 
                Stock.id, 

                Stock_price.date, 
                Stock_price.close, 
                Stock_price.sma_20, 
                Stock_price.sma_50, 
                Stock_price.rsi_14
            ).filter(
                Stock_price.date == max_date
            ).order_by(
                asc(Stock.symbol)
            ).all()

    from .models import Filter
    filters = Filter.query.all()

    return render_template(
        "index.html",
        request=request,
        title = 'Stock',
        trading=stocks,
        user=current_user,
        filters=filters
    )

@stock_views.route("/stock/<symbol>", methods=['GET', 'POST'])
@login_required
def stock_detail(symbol):

    # # init database
    # [cursor, connection] = helpers.init_database()
    from .models import Stock, Market, Strategy, Stock_strategy, Stock_price
    stock = db.session.query(
            Stock
        ).join(
            Market, 
            Market.id == Stock.market_id
        ).with_entities(
            Stock.name, 
            Stock.symbol, 
            Stock.id, 

            Market.name.label('market_name'),
            Market.market_close_local,
            Market.market_open_local
        ).filter(
            Stock.symbol == symbol
        ).order_by(
            asc(Stock.symbol)
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
    stocks = {}

    for strategy in strategies:
        temp = db.session.execute("SELECT * from stock_strategy\
            join " + strategy.params + " on " + strategy.params + ".parameter_id = stock_strategy.parameter_id and " + strategy.params + ".trading_id = stock_strategy.stock_id\
            where stock_strategy.stock_id = "+str(stock.id)+" and stock_strategy.strategy_id = "+ str(strategy.id))

        stats = []
        for x in temp:
            stats.append(x)
        parameters[strategy.name] = stats
                            
        temp_stock_ids = db.session.query(
            Stock_strategy
        ).with_entities(
            Stock_strategy.stock_id
        ).filter(
            Stock_strategy.strategy_id == strategy.id
        ).order_by(
            asc(Stock_strategy.id)
        ).all()

        # convert stock-id's in an array and write array in List
        stock_id = []
        for temp_stock_id in temp_stock_ids:
            stock_id.append(temp_stock_id.stock_id)
        stocks[strategy.name] = stock_id

    bars = db.session.query(
            Stock_price
        ).filter(
            Stock_price.stock_id == stock.id
        ).order_by(
            desc(Stock_price.date)
        ).all()
        
    return render_template(
        "trading_detail.html",
        user = current_user,
        request = request, 
        title = "Stock",
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

@stock_views.route("/apply_strategy", methods=['GET', 'POST'])
@login_required
def apply_strategy():

    strategy_name = request.form.get('strategy_name')
    stock_id = request.form.get('stock_id')
    trade_price = request.form.get('trade_price')
    observe_from = request.form.get('observe_from')
    observe_until = request.form.get('observe_until')
    period = request.form.get('period')
    stddev = request.form.get('stddev')

    from .models import Strategy, Stock_strategy, Trading, Param_stock_strategy_breakdown, Param_stock_strategy_breakout, Param_stock_strategy_bollinger

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
            Trading.trading == "STC"
        ).first()

    # insert parameters into database
    
    if strategy.params == "param_stock_strategy_breakdown":

        new_param_breakdown = Param_stock_strategy_breakdown(trading_id = stock_id, observe_from = observe_from, observe_until = observe_until, trade_price = trade_price, trading = trading.id)
        db.session.add(new_param_breakdown)
        db.session.commit()
    
    elif strategy.params == "param_stock_strategy_breakout":

        new_param_breakout = Param_stock_strategy_breakout(trading_id = stock_id, observe_from = observe_from, observe_until = observe_until, trade_price = trade_price, trading = trading.id)
        print(f"Observe Until 222: {observe_until}")
        db.session.add(new_param_breakout)
        db.session.commit()

    elif strategy.params == "param_stock_strategy_bollinger":

        new_param_bollinger = Param_stock_strategy_bollinger(trading_id = stock_id, period = period, stddev = stddev, trade_price = trade_price, trading = trading.id)
        db.session.add(new_param_bollinger)
        db.session.commit()

    try:
        parameter_id = db.session.execute("select * from " + strategy.params + " where parameter_id = (select max(parameter_id) from " + strategy.params + ")").first().parameter_id
    except Exception as e:
        parameter_id = 0

    # insert stock_strategy into database
    new_stock_strategy = Stock_strategy(stock_id = stock_id, strategy_id = strategy.id, parameter_id = parameter_id, is_traded = True)
    db.session.add(new_stock_strategy)
    db.session.commit()

    return redirect(url_for('stock_views.strategy', strategy_name = strategy.name, mode = 'applied'))

@stock_views.route("/strategies", methods = ['GET', 'POST'])
@login_required
def strategies():

    from .models import Strategy

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

    return render_template(
        "strategies.html",
        title = "Stock",
        user = current_user,
        request = request,
        strategies = strategies
    )

@stock_views.route("/strategy/<strategy_name>/<mode>")
@login_required
def strategy(strategy_name, mode):

    from .models import Strategy, Trading

    strategy = db.session.query(
        Strategy
    ).filter(
        Strategy.name == strategy_name
    ).first()

    trading = db.session.query(
            Trading
        ).filter(
            Trading.trading == "Stock"
        ).first()

    print(trading.id)

    applied_stocks = db.session.execute("SELECT * from " + strategy.params + "\
        join stock_strategy on " + strategy.params + ".parameter_id = stock_strategy.parameter_id and " + strategy.params + ".trading_id = stock_strategy.stock_id\
        join stock on stock.id = stock_strategy.stock_id\
        where stock_strategy.strategy_id = " + str(strategy.id) + " and " + strategy.params + ".trading = "+ str(trading.id)+"\
        GROUP BY stock_strategy.parameter_id\
        ORDER BY symbol")

    saved_stocks = db.session.execute("SELECT * from " + strategy.params + "\
        join stock_strategy on " + strategy.params + ".parameter_id = stock_strategy.parameter_id and " + strategy.params + ".trading_id = stock_strategy.stock_id\
        join stock on stock.id = " + strategy.params + ".trading_id\
        where " + strategy.params + ".trading = "+ str(trading.id)+"\
        ORDER BY id")

    list_applied_stocks = []
    list_stocks_applied = []
    for stock in applied_stocks:
        list_applied_stocks.append(stock.parameter_id) # parameter ids of the stocks
        list_stocks_applied.append(stock) # 

    list_saved_stocks = []
    list_stocks_saved = []
    is_traded = {}
    for stock in saved_stocks:
        list_saved_stocks.append(stock.parameter_id) # parameter ids of the stocks
        list_stocks_saved.append(stock) # 
        if stock.parameter_id in list_applied_stocks:
            is_traded[stock.parameter_id] = True
        else:
            is_traded[stock.parameter_id] = False

    if mode == 'applied':
        stocks = list_stocks_applied

    if mode == 'saved':
        stocks = list_stocks_saved

    return render_template(
        "strategy.html",
        title = 'Stock',
        user = current_user,
        request = request,
        trading = stocks,
        strategy = strategy,
        mode = mode,
        is_traded = is_traded
    )

@stock_views.route("/delete_traded_strategy", methods=['GET', 'POST'])
@login_required
def delete_traded_strategy():

    stock_id = request.form.get('trading_id')
    strategy_name = request.form.get('strategy_name')
    strategy_id = request.form.get('strategy_id')
    parameter_id = request.form.get('parameter_id')

    from .models import Stock_strategy

    stock = db.session.query(Stock_strategy).filter_by(strategy_id = strategy_id, parameter_id = parameter_id, stock_id = stock_id)
    stock.delete()
    db.session.commit()

    return redirect(url_for('stock_views.strategy', strategy_name = strategy_name, mode = 'applied'))

@stock_views.route("/apply_saved_strategies/<strategy_name>", methods=['GET', 'POST'])
@login_required
def apply_saved_strategies(strategy_name):

    from .models import Stock_strategy
    
    array = request.args.get('parameters_to_apply')
    strategy_id = request.args.get('strategy_id')

    # # parse array:
    array_parsed = json.loads(array)
    print(array_parsed)

    saved_stocks = db.session.query(Stock_strategy).filter_by(strategy_id = strategy_id).all()

    print(f"Saved Stocks 1: {saved_stocks}")

    applied_parameters_on_strategy = []
    for stock in saved_stocks:
        applied_parameters_on_strategy.append(stock.parameter_id)

    # look to insert
    for parsed in array_parsed:
        stock_id = array_parsed[parsed]['trading_id']
        parameter_id = parsed
        print(parameter_id)

        try:
            b=applied_parameters_on_strategy.index(int(parameter_id))
        except ValueError:
            new_stock_strategy = Stock_strategy(stock_id=stock_id, strategy_id=strategy_id, parameter_id = parameter_id, is_traded = True)
            db.session.add(new_stock_strategy)
            db.session.commit()

    # look to remove
    for saved in saved_stocks:
        print(f"Hallo: {saved.parameter_id}")
        if str(saved.parameter_id) not in array_parsed:
            print(f"Hallo: ")

            db.session.query(Stock_strategy).filter_by(strategy_id = saved.strategy_id, parameter_id = saved.parameter_id, stock_id = saved.stock_id).update({"is_traded": False})
            db.session.commit()

    return redirect(url_for('stock_views.strategy', strategy_name = strategy_name, mode = 'saved'))
