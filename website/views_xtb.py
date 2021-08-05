from flask import Blueprint, render_template, request, redirect, url_for

from flask_login import login_required, current_user

from .extensions import db

from sqlalchemy import desc, asc, func

views_xtb = Blueprint('views_xtb', __name__)


@views_xtb.route('/index/<trading>', methods=['GET', 'POST'])
@login_required
def index(trading):
    # read data from request
    stock_filter = request.args.get('filter')
    rsi_ob = request.args.get('rsi_ob')
    rsi_os = request.args.get('rsi_os')

    from .models import Symbol_XTB_price, Trading
    max_date = db.session.query(func.max(Symbol_XTB_price.date)).first()[0]

    stocks = []

    trading_id = db.session.query(
        Trading
    ).filter(
        Trading.trading == trading
    ).first().id

    print(f"trading: {trading}")
    print(f"trading id: {trading_id}")

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
                Symbol_XTB.trading_id == trading_id
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
                Symbol_XTB.trading_id == trading_id
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
                Symbol_XTB.trading_id == trading_id
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
                Symbol_XTB.trading_id == trading_id
            ).order_by(
                asc(
                    Symbol_XTB.symbol
                )
            ).all()

    else:
        from .models import Symbol_XTB, Symbol_XTB_price

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
                Symbol_XTB.trading_id == trading_id
            ).order_by(
                asc(Symbol_XTB.symbol)
            ).all()

    from .models import Filter
    filters = Filter.query.all()

    return render_template(
        "index.html",
        request=request,
        title = 'Stock',
        broker = 'xtb',
        trading=stocks,
        user=current_user,
        filters=filters
    )


@views_xtb.route("/symbol/<symbol>", methods=['GET', 'POST'])
@login_required
def stock_detail(symbol):

    # # init database
    # [cursor, connection] = helpers.init_database()
    from .models import Symbol_XTB, Week, Strategy, Stock_strategy, Symbol_XTB_price
    stock = db.session.query(
            Symbol_XTB
        ).join(
            Week, 
            Week.id == Symbol_XTB.week_id
        ).with_entities(
            Symbol_XTB.description.label('name'), 
            Symbol_XTB.symbol, 
            Symbol_XTB.id, 

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
            Symbol_XTB.symbol == symbol
        ).order_by(
            asc(Symbol_XTB.symbol)
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
        
    return render_template(
        "trading_detail.html",
        user = current_user,
        request = request, 
        title = "Stock",
        broker = 'xtb',
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