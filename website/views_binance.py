from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .extensions import db, alpaca_api
import json
from sqlalchemy import desc, asc, func

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

@views_binance.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # read data from request
    crypto_filter = request.args.get('filter')
    rsi_ob = request.args.get('rsi_ob')
    rsi_os = request.args.get('rsi_os')

    from .models import Crypto_price
    max_date = db.session.query(func.max(Crypto_price.date)).first()[0]

    # grab latest stock-data according filter
    if crypto_filter == 'new_closing_highs':

        from .models import Crypto, Crypto_price

        last_orders = db.session.query(
            Crypto_price.crypto_id, db.func.max(Crypto_price.close).label('max_close_Crypto')
        ).group_by(Crypto_price.crypto_id).subquery()

        Cryptos = db.session.query(
                Crypto_price
            ).join(
                Crypto, 
                Crypto.id == Crypto_price.crypto_id
            ).join(
                last_orders,
                last_orders.c.crypto_id == Crypto_price.crypto_id
            ).with_entities(
                Crypto.name, 
                Crypto.symbol, 
                Crypto.id, 

                Crypto_price.date, 
                last_orders.c.max_close_Crypto,
                Crypto_price.close, 
                Crypto_price.sma_20, 
                Crypto_price.sma_50, 
                Crypto_price.rsi_14
            ).filter(
                Crypto_price.close == last_orders.c.max_close_Crypto,
                Crypto_price.date == max_date
            ).order_by(
                asc(
                    Crypto.symbol
                )
            ).all()

    elif crypto_filter == 'new_closing_lows':

        last_orders = db.session.query(
            Crypto_price.crypto_id, db.func.min(Crypto_price.close).label('min_close_Crypto')
        ).group_by(Crypto_price.crypto_id).subquery()

        from .models import Crypto, Crypto_price

        Cryptos = db.session.query(
                Crypto_price
            ).join(
                Crypto, 
                Crypto.id == Crypto_price.crypto_id
            ).join(
                last_orders,
                last_orders.c.crypto_id == Crypto_price.crypto_id
            ).with_entities(
                Crypto.name, 
                Crypto.symbol, 
                Crypto.id, 

                Crypto_price.date, 
                last_orders.c.min_close_Crypto,
                Crypto_price.close, 
                Crypto_price.sma_20, 
                Crypto_price.sma_50, 
                Crypto_price.rsi_14
            ).filter(
                Crypto_price.close == last_orders.c.min_close_Crypto,
                Crypto_price.date == max_date
            ).order_by(
                asc(
                    Crypto.symbol
                )
            ).all()

    elif crypto_filter == 'rsi_overbought':

        from .models import Crypto, Crypto_price
        Cryptos = db.session.query(
                Crypto_price
            ).join(
                Crypto, 
                Crypto_price.crypto_id == Crypto.id
            ).with_entities(
                Crypto.name, 
                Crypto.symbol, 
                Crypto.id, 

                Crypto_price.date, 
                Crypto_price.close, 
                Crypto_price.sma_20, 
                Crypto_price.sma_50, 
                Crypto_price.rsi_14
            ).filter(
                Crypto_price.rsi_14 > str(rsi_ob),
                Crypto_price.date == max_date
            ).order_by(
                asc(
                    Crypto.symbol
                )
            ).all()

    elif crypto_filter == 'rsi_oversold':
        from .models import Crypto, Crypto_price
        Cryptos = db.session.query(
                Crypto_price
            ).join(
                Crypto, 
                Crypto_price.crypto_id == Crypto.id
            ).with_entities(
                Crypto.name, 
                Crypto.symbol, 
                Crypto.id, 

                Crypto_price.date, 
                Crypto_price.close, 
                Crypto_price.sma_20, 
                Crypto_price.sma_50, 
                Crypto_price.rsi_14
            ).filter(
                Crypto_price.rsi_14 < str(rsi_os),
                Crypto_price.date == max_date
            ).order_by(
                asc(
                    Crypto.symbol
                )
            ).all()

    else:
        from .models import Crypto, Crypto_price

        Cryptos = db.session.query(
                Crypto
            ).join(
                Crypto_price, 
                Crypto_price.crypto_id == Crypto.id
            ).with_entities(
                Crypto.name, 
                Crypto.symbol, 
                Crypto.id, 

                Crypto_price.date, 
                Crypto_price.close, 
                Crypto_price.sma_20, 
                Crypto_price.sma_50, 
                Crypto_price.rsi_14
            ).filter(
                Crypto_price.date == max_date
            ).order_by(
                asc(Crypto.symbol)
            ).all()

    from .models import Filter
    filters = Filter.query.all()

    return render_template(
        "index.html",
        request=request,
        title = 'Crypto',
        broker = 'binance',
        trading=Cryptos,
        user=current_user,
        filters=filters
    )

@views_binance.route("/crypto/<symbol>", methods=['GET', 'POST'])
@login_required
def crypto_detail(symbol):

    print(symbol)

    # # init database
    # [cursor, connection] = helpers.init_database()
    from .models import Crypto, Strategy, Crypto_strategy, Crypto_price
    crypto = db.session.query(
            Crypto
        ).with_entities(
            Crypto.name, 
            Crypto.symbol, 
            Crypto.id, 
        ).filter(
            Crypto.symbol == symbol
        ).order_by(
            asc(Crypto.symbol)
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
        temp = db.session.execute("SELECT * from crypto_strategy\
            join " + strategy.params + " on " + strategy.params + ".parameter_id = crypto_strategy.parameter_id and " + strategy.params + ".trading_id = crypto_strategy.crypto_id\
            where crypto_strategy.crypto_id = "+str(crypto.id)+" and crypto_strategy.strategy_id = "+ str(strategy.id))

        stats = []
        for x in temp:
            stats.append(x)
        parameters[strategy.name] = stats
                            
        temp_crypto_ids = db.session.query(
            Crypto_strategy
        ).with_entities(
            Crypto_strategy.crypto_id
        ).filter(
            Crypto_strategy.strategy_id == strategy.id
        ).order_by(
            asc(Crypto_strategy.id)
        ).all()

        # convert stock-id's in an array and write array in List
        crypto_id = []
        for temp_crypto_id in temp_crypto_ids:
            crypto_id.append(temp_crypto_id.crypto_id)
        cryptos[strategy.name] = crypto_id

    bars = db.session.query(
            Crypto_price
        ).filter(
            Crypto_price.crypto_id == crypto.id
        ).order_by(
            desc(Crypto_price.date)
        ).all()
        
    return render_template(
        "trading_detail.html",
        user = current_user,
        request = request, 
        title = "Crypto",
        broker = 'binance',
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
    stock_id = request.form.get('stock_id')
    trade_price = request.form.get('trade_price')
    observe_from = request.form.get('observe_from')
    observe_until = request.form.get('observe_until')
    period = request.form.get('period')
    stddev = request.form.get('stddev')

    from .models import Strategy, Crypto_strategy, Trading, Param_stock_strategy_breakdown, Param_stock_strategy_breakout, Param_stock_strategy_bollinger

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
        Trading.trading == "CRT"
    ).first()

    # insert parameters into database

    if strategy.params == "param_stock_strategy_breakdown":

        new_param_breakdown = Param_stock_strategy_breakdown(trading_id = stock_id, observe_from = observe_from, observe_until = observe_until, trade_price = trade_price, trading = trading.id)
        db.session.add(new_param_breakdown)
        db.session.commit()
    
    elif strategy.params == "param_stock_strategy_breakout":

        new_param_breakout = Param_stock_strategy_breakout(trading_id = stock_id, observe_from = observe_from, observe_until = observe_until, trade_price = trade_price, trading = trading.id)
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
    new_stock_strategy = Crypto_strategy(crypto_id = stock_id, strategy_id = strategy.id, parameter_id = parameter_id, is_traded = True)
    db.session.add(new_stock_strategy)
    db.session.commit()

    return redirect(url_for('views_binance.strategy', strategy_name = strategy.name, mode = 'applied'))

@views_binance.route("/strategies", methods = ['GET', 'POST'])
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
        title = "Crypto",
        broker = 'binance',
        user = current_user,
        request = request,
        strategies = strategies
    )

@views_binance.route("/strategy/<strategy_name>/<mode>")
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
        Trading.trading == "Crypto"
    ).first()

    applied_cryptos = db.session.execute("SELECT * from " + strategy.params + "\
    join crypto_strategy on " + strategy.params + ".parameter_id = crypto_strategy.parameter_id and " + strategy.params + ".trading_id = crypto_strategy.crypto_id\
    join crypto on crypto.id = crypto_strategy.crypto_id\
    where crypto_strategy.strategy_id = " + str(strategy.id) + " and " + strategy.params + ".trading = "+str(trading.id)+"\
    GROUP BY crypto_strategy.parameter_id\
    ORDER BY symbol")

    saved_cryptos = db.session.execute("SELECT * from " + strategy.params + "\
        join crypto on crypto.id = " + strategy.params + ".trading_id\
        where " + strategy.params + ".trading = "+str(trading.id)+"\
        ORDER BY id")

    list_applied_cryptos = []
    list_cryptos_applied = []
    for crypto in applied_cryptos:
        list_applied_cryptos.append(crypto.parameter_id) # parameter ids of the stocks
        list_cryptos_applied.append(crypto) # 
        print(f"Applied: {crypto}")

    list_saved_cryptos = []
    list_cryptos_saved = []
    is_traded = {}
    for crypto in saved_cryptos:
        list_saved_cryptos.append(crypto.parameter_id) # parameter ids of the stocks
        list_cryptos_saved.append(crypto) # 
        if crypto.parameter_id in list_applied_cryptos:
            is_traded[crypto.parameter_id] = True
        else:
            is_traded[crypto.parameter_id] = False
        print(f"saved: {crypto}")

    if mode == 'applied':
        cryptos = list_cryptos_applied

    if mode == 'saved':
        cryptos = list_cryptos_saved

    return render_template(
        "strategy.html",
        title = 'Crypto',
        broker = 'binance',
        user = current_user,
        request = request,
        trading = cryptos,
        strategy = strategy,
        mode = mode,
        is_traded = is_traded
    )

@views_binance.route("/delete_traded_strategy", methods=['GET', 'POST'])
@login_required
def delete_traded_strategy():

    crypto_id = request.form.get('trading_id')
    strategy_name = request.form.get('strategy_name')
    strategy_id = request.form.get('strategy_id')
    parameter_id = request.form.get('parameter_id')

    from .models import Crypto_strategy

    crypto = db.session.query(Crypto_strategy).filter_by(strategy_id = strategy_id, parameter_id = parameter_id, crypto_id = crypto_id)
    crypto.delete()
    db.session.commit()

    return redirect(url_for('views_binance.strategy', strategy_name = strategy_name, mode = 'applied'))


@views_binance.route("/apply_saved_strategies/<strategy_name>", methods=['GET', 'POST'])
@login_required
def apply_traded_strategy(strategy_name):

    from .models import Crypto_strategy

    array = request.args.get('parameters_to_apply')
    strategy_id = request.args.get('strategy_id')

    # # parse array:
    array_parsed = json.loads(array)
    print(f"array_parsed: {array_parsed}")

    saved_cryptos = db.session.query(Crypto_strategy).filter_by(strategy_id = strategy_id).all()

    print(f"Saved Cryptos 1: {saved_cryptos}")

    applied_parameters_on_strategy = []
    for crypto in saved_cryptos:
        applied_parameters_on_strategy.append(crypto.parameter_id)

    # look to insert
    for parsed in array_parsed:
        crypto_id = array_parsed[parsed]['trading_id']
        parameter_id = parsed
        print(parameter_id)

        try:
            b=applied_parameters_on_strategy.index(int(parameter_id))
        except ValueError:
            new_crypto_strategy = Crypto_strategy(crypto_id=crypto_id, strategy_id=strategy_id, parameter_id = parameter_id, is_traded = True)
            db.session.add(new_crypto_strategy)
            db.session.commit()

    # look to remove
    for saved in saved_cryptos:
        if str(saved.parameter_id) not in array_parsed:
            print(f"Hallo: ")
            crypto = db.session.query(Crypto_strategy).filter_by(strategy_id = saved.strategy_id, parameter_id = saved.parameter_id, crypto_id = saved.crypto_id)
            crypto.delete()
            db.session.commit()

    return redirect(url_for('views_binance.strategy', strategy_name = strategy_name, mode = 'saved'))
