from sqlalchemy import func

class database(object):

    def populate_user():
        from .models import User
        from .extensions import db

        new_user = User(email = "kim.schenk@hotmail.com", password = "sha256$EN5U9Q8G$46e100accf6ba8832e22753ba6e04034cfca0e7dde604f2bc71f41c428ab52bc", first_name = "kim")
        db.session.add(new_user)
        db.session.commit()

    def populate_trading():
        from .models import Trading
        from .extensions import db, xtb_api

        tradings=db.session.query(
            Trading
        ).all()

        category_names = [trading.trading for trading in tradings]
        symbols_xtb = xtb_api.get_all_symbols()

        for symbol in symbols_xtb:
            try:
                asset_category = symbol['categoryName']
                asset_symbol = symbol['symbol']
                if asset_category not in category_names:
                    category_names.append(asset_category)
                    new_trading = Trading(trading = asset_category)
                    db.session.add(new_trading)
                    db.session.commit()
                    print(f"Added a new bond: {asset_category}")

            except Exception as e:
                print(f"Exception: {asset_symbol}")
                print(e)

        print("...populated tradings...")

    def populate_strategies():

        from .models import Strategy
        from .extensions import db

        strategies = ['opening_range_breakout', 'opening_range_breakdown', 'bollinger_bands']
        parameters = ['param_stock_strategy_breakout', 'param_stock_strategy_breakdown', 'param_stock_strategy_bollinger']
        urls = ['https://preview.redd.it/5hr25h8tf3n61.png?width=1800&format=png&auto=webp&s=0bd3665b1caf5e1907833734830efc515d25d1c8', 'https://preview.redd.it/ayr4fmcuf3n61.png?width=1794&format=png&auto=webp&s=6f5a9e5edb052c87d16d74e6113e45d0a6b18b5b', 'https://i0.wp.com/www.dolphintrader.com/wp-content/uploads/2013/03/bollingerbands-Awesome1.gif?resize=620%2C550']

        for strat in strategies:
            new_strategy = Strategy(name=strat, params=parameters[strategies.index(strat)], url_pic=urls[strategies.index(strat)])
            db.session.add(new_strategy)
            db.session.commit()

        print("...populated strategies...")

    def populate_filters():

        from .models import Filter
        from .extensions import db

        filters = ['new_closing_highs', 'new_closing_lows', 'rsi_overbought', 'rsi_oversold']

        for filter in filters:
            new_filter = Filter(name=filter)
            db.session.add(new_filter)
            db.session.commit()
        print("...populated filters...")


    def populate_alpaca_market():
        from .models import Market
        from .extensions import db

        markets=db.session.query(Market).all()
        market_list = [market.name for market in markets]

        import csv
        # Read markets.csv to add new markets
        new_markets = []
        with open('website/markets.csv') as f:
            reader = csv.reader(f)
            for line in reader:
                new_markets.append(line)

        # For all new markets:
        for new_market in new_markets:
            if new_market[1] not in market_list:                    # If name of new market not in database yet, add it
                try:
                    print(f"Add a new market: {new_market[0]}, {new_market[1]}")
                    new_market = Market(exchange=new_market[0], name=new_market[1], market_open_local=new_market[2], market_close_local=new_market[3], timezone=new_market[4])
                    db.session.add(new_market)
                    db.session.commit()           
                except Exception as e:
                    print(f"Exception: {new_market[0]}")
                    print(e)
            else:
                print(f"Already existing, skipped {new_market[0]}")

        print("...populated markets...")

    def populate_alpaca_stocks():
        from .models import Stock, Market, Trading, Trading
        from .extensions import db, alpaca_api

        trading_id = db.session.query(
            Trading
        ).filter(
            Trading.trading == "STC"
        ).first().id

        print(trading_id)

        stocks=db.session.query(Stock).all()
        symbols = [stock.symbol for stock in stocks]

        assets = alpaca_api.list_assets()

        chunk_size = 100

        for i in range(0, len(assets), chunk_size):
            symbol_chunk = assets[i:i+chunk_size]

            for asset in symbol_chunk:
                try:
                    if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
                        market_id = Market.query.filter_by(exchange=asset.exchange).first().id
                        print(f"Add a new alpaca symbol: {asset.exchange} {asset.symbol} {asset.name}")
                        new_stock = Stock(symbol=asset.symbol, name=asset.name, market_id=market_id, shortable=asset.shortable, trading_id = trading_id)
                        db.session.add(new_stock)
                except Exception as e:
                    print(f"Exception: {asset.symbol}")
                    print(e)
            db.session.commit()
    
        print("...populated alpaca stocks...")

    def populate_alpaca_stock_prices():

        from website import config
        import alpaca_trade_api as tradeapi
        import tulipy, numpy
        from datetime import date, datetime
        from .models import Stock, Stock_price
        from .extensions import db

        # https://www.youtube.com/watch?v=Ni8mqdUXH3g

        stocks=Stock.query.all()

        symbols = []
        stock_dict = {}
        for stock in stocks:
            symbol = stock.symbol
            symbols.append(symbol)
            stock_dict[symbol] = stock.id

        api = tradeapi.REST(config.API_KEY_ALPACA, config.API_SECRET_ALPACA, base_url=config.API_URL_ALPACA)

        current_date = date.today().isoformat()

        chunk_size = 200
        for i in range(0, len(symbols), chunk_size):
            symbol_chunk = symbols[i:i+chunk_size]
            barsets = api.get_barset(symbol_chunk, 'day', start=current_date, end=current_date)

            for symbol in barsets:
                stock_id = stock_dict[symbol]
                print(symbol)
                date = db.session.query(func.max(Stock_price.date)).filter(Stock_price.stock_id==stock_id).scalar()
                close_done = []

                try:
                    max_date = datetime.strptime(date, '%Y-%m-%d').date().isoformat()

                except Exception as e:
                    # print(f"No data {e}")
                    max_date = datetime.strptime('2000-01-01', '%Y-%m-%d').date().isoformat()

                for bar in barsets[symbol]:
                    bar_date = bar.t.date().isoformat()
                    close_done.append(bar.c)

                    if bar_date > max_date and bar_date < current_date:
                        sma_20, sma_50, rsi_14 = None, None, None

                        if len(close_done) > 20:
                            sma_20 = tulipy.sma(numpy.array(close_done), period=20)[-1]

                        if len(close_done) > 50:
                            sma_50 = tulipy.sma(numpy.array(close_done), period=50)[-1]

                        if len(close_done) > 14:
                            rsi_14 = tulipy.rsi(numpy.array(close_done), period=14)[-1]
                                                        
                        try:
                            new_stock_price = Stock_price(stock_id=stock_id, date=bar.t.date(), open=bar.o, high=bar.h, low=bar.l, close=bar.c, volume=bar.v, sma_20=sma_20, sma_50=sma_50, rsi_14=rsi_14)
                            db.session.add(new_stock_price)
                            # print(f"added price to {symbol}")

                        except Exception as e:
                            print(f"No stock-price added: {e}")

            db.session.commit()


        # candles = xtb_api.get_chart_range_request(end = 1262944412000,  period = 5, start=1262944112000, symbol="PKN.PL", ticks=0)
        
        # for candle in candles:
        #     print(candle['close'])

        print("...populated stock prices...")


    def test():
        
        from .extensions import xtb_api

        candles = xtb_api.get_chart_range_request(end = 1262944412,  period = 5, start=1262944112, symbol="PKN.PL", ticks=0)
        
        for candle in candles:
            print(candle['close'])

        print("...populated alpaca stocks...")


    def calculate(symbol):
        week = [None] * 14

        print(symbol['symbol'])

        for day in symbol['trading']:
            fromT = day['fromT']
            hours1 = int(fromT/3600)
            left = fromT - hours1*3600
            if hours1 <= 9:
                hours1 = '0' + str(hours1)
            minutes1 = int(left/60)
            if minutes1 <= 9:
                minutes1 = '0' + str(minutes1)

            toT = day['toT']
            hours2 = int(toT/3600)
            left = toT - hours2*3600
            if hours2 <= 9:
                hours2 = '0' + str(hours2)
            minutes2 = int(left/60)
            if minutes2 <= 9:
                minutes2 = '0' + str(minutes2)

            if week[2*(day['day']-1)] == None:
                week[2*(day['day']-1)] = [f"{hours1}:{minutes1}",f"{hours2}:{minutes2}"]
                week[2*(day['day']-1)+1] = [f"-",f"-"]
                
            else:
                if week[2*(day['day']-1)][0] < f"{hours1}:{minutes1}":
                    week[2*(day['day']-1)+1] = [f"{hours1}:{minutes1}",f"{hours2}:{minutes2}"]
                else:
                    week[2*(day['day']-1)+1] = week[2*(day['day']-1)]
                    week[2*(day['day']-1)] = [f"{hours1}:{minutes1}",f"{hours2}:{minutes2}"]

        for day in week:
            if day == None:
                number = week.index(day)
                week[number] = ["00:00", "00:00"]
                
        return week

    def populate_xtb_symbols_and_market():
        from .models import Symbol_XTB, Trading, Week
        from .extensions import db, xtb_api

        symbols=db.session.query(Symbol_XTB).all()
        symbol_list = [symbol.symbol for symbol in symbols]

        weeks = db.session.query(Week).all()
        list_weeks = [[[week.Monday, week.Monday2],[week.Tuseday, week.Tuseday2],[week.Wednesday, week.Wednesday2],[week.Thursday, week.Thursday2],[week.Friday, week.Friday2],[week.Saturday, week.Saturday2],[week.Sunday, week.Sunday2]] for week in weeks]
        print(list_weeks)

        # list to use symbols parameters when looking for trading hours
        list_symbols = {}
        # array to loop through the stocks
        array_symbols = []

        # CHECK IF MARKET IS OPEN FOR EURUSD
        symbols_xtb = xtb_api.get_all_symbols()
        for symbol in symbols_xtb:
                asset_category = symbol['categoryName']
                asset_description = symbol['description']
                asset_currency = symbol['currency']
                asset_trailing_en = symbol['trailingEnabled']
                asset_symbol = symbol['symbol']
                array_symbols.append(asset_symbol)
                list_symbols[asset_symbol] = {'asset_category': asset_category, 'asset_description': asset_description, 'asset_currency': asset_currency, 'asset_trailing_en': asset_trailing_en}

        chunk_size = 100

        for i in range(0, len(array_symbols), chunk_size):
            symbol_chunk = array_symbols[i:i+chunk_size]

            trading_hours = xtb_api.get_trading_hours(symbol_chunk)

            for symbol in trading_hours:
                if symbol['symbol'] not in symbol_list:

                    week = database.calculate(symbol)

                    if week not in list_weeks:
                        list_weeks.append(week)

                        new_Week = Week(
                            name = "Test", 
                            Monday = f"{week[0][0]}-{week[0][1]}", 
                            Monday2 = f"{week[1][0]}-{week[1][1]}", 
                            Tuseday = f"{week[2][0]}-{week[2][1]}", 
                            Tuseday2 = f"{week[3][0]}-{week[3][1]}", 
                            Wednesday = f"{week[4][0]}-{week[4][1]}", 
                            Wednesday2 = f"{week[5][0]}-{week[5][1]}", 
                            Thursday = f"{week[6][0]}-{week[6][1]}", 
                            Thursday2 = f"{week[7][0]}-{week[7][1]}", 
                            Friday = f"{week[8][0]}-{week[8][1]}", 
                            Friday2 = f"{week[9][0]}-{week[9][1]}", 
                            Saturday = f"{week[10][0]}-{week[10][1]}", 
                            Saturday2 = f"{week[11][0]}-{week[11][1]}", 
                            Sunday = f"{week[12][0]}-{week[12][1]}",
                            Sunday2 = f"{week[13][0]}-{week[13][1]}"
                            )

                        db.session.add(new_Week)
                        db.session.commit()

                    id = db.session.query(
                        Week
                    ).filter_by(
                        Monday = f"{week[0][0]}-{week[0][1]}", 
                        Monday2 = f"{week[1][0]}-{week[1][1]}", 
                        Tuseday = f"{week[2][0]}-{week[2][1]}", 
                        Tuseday2 = f"{week[3][0]}-{week[3][1]}", 
                        Wednesday = f"{week[4][0]}-{week[4][1]}", 
                        Wednesday2 = f"{week[5][0]}-{week[5][1]}", 
                        Thursday = f"{week[6][0]}-{week[6][1]}", 
                        Thursday2 = f"{week[7][0]}-{week[7][1]}", 
                        Friday = f"{week[8][0]}-{week[8][1]}", 
                        Friday2 = f"{week[9][0]}-{week[9][1]}", 
                        Saturday = f"{week[10][0]}-{week[10][1]}", 
                        Saturday2 = f"{week[11][0]}-{week[11][1]}", 
                        Sunday = f"{week[12][0]}-{week[12][1]}",
                        Sunday2 = f"{week[13][0]}-{week[13][1]}"
                    ).first().id

                    try:
                        asset_symbol = symbol['symbol']
                        if asset_symbol not in symbol_list:
                            asset_category = list_symbols[asset_symbol]['asset_category']
                            trading_id = db.session.query(
                                Trading
                            ).filter(
                                Trading.trading == asset_category
                            ).first()
                            asset_description = list_symbols[symbol['symbol']]['asset_description']
                            asset_currency = list_symbols[symbol['symbol']]['asset_currency']
                            asset_trailing_en = list_symbols[symbol['symbol']]['asset_trailing_en']
                            
                            new_symbol = Symbol_XTB(symbol=asset_symbol, trading_id = trading_id.id, description=asset_description, currency=asset_currency, trailing_enabled = asset_trailing_en, week_id = id)
                            db.session.add(new_symbol)
                            db.session.commit()

                            print(f"Add new xtb symbol: {asset_symbol}")
                        
                    except Exception as e:
                        print(f"Exception: {asset_symbol}")
                        print(e)
                        
        # trade = "TSLA.US_9"

        # # # CHECK IF MARKET IS OPEN FOR EURUSD
        # # xtb_api.get_commission(trade,1.0)
        # # # CHECK IF MARKET IS OPEN FOR EURUSD
        # xtb_api.get_symbol(trade)
        # # # CHECK IF MARKET IS OPEN FOR EURUSD
        # # xtb_api.check_if_market_open([trade])
        # # # # BUY ONE VOLUME (FOR EURUSD THAT CORRESPONDS TO 100000 units)
        # # xtb_api.open_trade('buy', trade, 1)
        # # SEE IF ACTUAL GAIN IS ABOVE 100 THEN CLOSE THE TRADE
        # trades = xtb_api.update_trades() # GET CURRENT TRADES
        # trade_ids = [trade_id for trade_id in trades.keys()]
        # for trade in trade_ids:
        #     actual_profit = xtb_api.get_trade_profit(trade) # CHECK PROFIT
        #     if actual_profit >= 100:
        #         xtb_api.close_trade(trade) # CLOSE TRADE
        # # CLOSE ALL OPEN TRADES
        # xtb_api.close_all_trades()
        # # THEN LOGOUT
        # xtb_api.logout()
        

        print("...populated xtb symbols...")

    def test_XY():
        from .extensions import xtb_api
        import datetime, time
        from datetime import date
        import time
        import datetime
        import tulipy, numpy
        from .models import Symbol_XTB, Symbol_XTB_price
        from .extensions import db
        from sqlalchemy import func

        # s = "1800-08-02T14:45:00"
        e = "2020-08-02T15:00:00"

        # https://www.youtube.com/watch?v=Ni8mqdUXH3g

        symbols_xtb=Symbol_XTB.query.all()

        symbols = []
        symbol_dict = {}
        for trading in symbols_xtb:
            symbol = trading.symbol
            # print(symbol)
            symbols.append(symbol)
            symbol_dict[symbol] = trading.id

        current_date = date.today().isoformat()

        for symbol in symbols:
            bars = xtb_api.get_range_candle_history(symbol = symbol, start = 0, end = time.time(), period = 1440, ticks = 0)

            symbol_id = symbol_dict[symbol]

            date1 = db.session.query(func.max(Symbol_XTB_price.date)).filter(Symbol_XTB_price.symbol_id==symbol_id).scalar()

            try:
                max_date = datetime.datetime.strptime(date1, '%Y-%m-%d').date().isoformat()
            except Exception as e:
                print(f"No data {e}")
                max_date = datetime.datetime.strptime('2000-01-01', '%Y-%m-%d').date().isoformat()

            close_done = []
            for bar in bars:

                bar_date = datetime.datetime.fromtimestamp(int(bar['timestamp'])).strftime("%Y-%m-%d")
                # print(f"bar_date: {bar_date}")
                close_done.append(bar['close'])
                if bar_date > max_date and bar_date < current_date:
                    sma_20, sma_50, rsi_14 = None, None, None

                    if len(close_done) > 20:
                        sma_20 = tulipy.sma(numpy.array(close_done), period=20)[-1]
                    if len(close_done) > 50:
                        sma_50 = tulipy.sma(numpy.array(close_done), period=50)[-1]
                    if len(close_done) > 14:
                        rsi_14 = tulipy.rsi(numpy.array(close_done), period=14)[-1]
                        
                    try:
                        new_stock_price = Symbol_XTB_price(symbol_id=symbol_id, date=bar_date, open=bar['open'], high=bar['high'], low=bar['low'], close=bar['close'], volume=bar['volume'], sma_20=sma_20, sma_50=sma_50, rsi_14=rsi_14)
                        db.session.add(new_stock_price)
                        # print(f"added price to {symbol}")

                    except Exception as e:
                        print(f"exception: {e}")

            db.session.commit()

        print("...populated stock prices...")


    def populate_cryptos():

        from website import config
        from binance.client import Client
        from .models import Crypto
        from .extensions import db

        cryptos = Crypto.query.all()
        symbols = [crypto.symbol for crypto in cryptos]

        # Login to Client
        client = Client(api_key=config.api_key, api_secret=config.api_secret)
        client2 = Client(api_key=config.api_key2, api_secret=config.api_secret2)

        # Set Test-URL in case of testnet.binance
        if config.test_mode:
            client.API_URL = config.API_URL_BINANCE
        else:
            client2.API_URL = config.API_URL_BINANCE

        exchange_info = client.get_exchange_info()
        # print(exchange_info)
        
        symbols=exchange_info['symbols']
        for symbol in symbols:
            print(symbol)
            print(symbol['symbol'])

            try:
                if symbol['status'] == 'TRADING' and symbol['symbol'] not in symbols:
                    print(f"Added a new crypto: {symbol['symbol']}")
                    new_crypto = Crypto(symbol=symbol['symbol'], name=symbol['baseAsset'])
                    db.session.add(new_crypto)
                    db.session.commit()
            except Exception as e:
                print(symbol['symbol'])
                print(e)
        print("...populated cryptos...")

    def populate_crypto_prices():

        from website import config
        from binance.client import Client
        import tulipy, numpy
        from datetime import date, datetime
        from .models import Crypto, Crypto_price
        from .extensions import db
        # https://www.youtube.com/watch?v=Ni8mqdUXH3g

        cryptos=Crypto.query.all()

        symbols = []
        crypto_dict = {}
        for crypto in cryptos:
            symbol = crypto.symbol
            symbols.append(symbol)
            crypto_dict[symbol] = crypto.id
        

        # Login to Client
        client = Client(api_key=config.api_key, api_secret=config.api_secret)
        client2 = Client(api_key=config.api_key2, api_secret=config.api_secret2)

        # Set Test-URL in case of testnet.binance
        if config.test_mode:
            client.API_URL = config.API_URL_BINANCE
        else:
            client2.API_URL = config.API_URL_BINANCE

        current_date = date.today().isoformat()

        for symbol in symbols:
            candlesticks = client2.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2012", "12 Jul, 2020")

            recent_closes = []
            print(recent_closes)
            crypto_id = crypto_dict[symbol]

            date = db.session.query(func.max(Crypto_price.date)).filter(Crypto_price.crypto_id==crypto_id).scalar()
            print(f"Date_max 1: {date}")

            try:
                max_date = datetime.strptime(date, '%Y-%m-%d').date().isoformat()
            except Exception as e:
                # print(f"No data {e}")
                max_date = datetime.strptime('2000-01-01', '%Y-%m-%d').date().isoformat()
            print(f"Date_max 2: {max_date}") 

            for candlestick in candlesticks:
                close = candlestick[4] # close
                recent_closes.append(float(close))

                close_time = candlestick[6] # timestamp unix
                bar_date = datetime.fromtimestamp(int(close_time/1000)).strftime('%Y-%m-%d')

                if bar_date > max_date and bar_date < current_date:

                    if len(recent_closes) >= 50:
                        sma_20 = tulipy.sma(numpy.array(recent_closes), period=20)[-1]
                        sma_50 = tulipy.sma(numpy.array(recent_closes), period=50)[-1]
                        rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14)[-1]
                    else:
                        sma_20, sma_50, rsi_14 = None, None, None
                        
                    try:

                        # open_time = candlestick[0] # timestamp unix
                        open = candlestick[1] # open
                        high = candlestick[2] # high
                        low = candlestick[3] # low
                        # close = candlestick[4] # close
                        volume = candlestick[5] # volume
                        # close_time = candlestick[6] # timestamp unix
                        # quote_asset_volume = candlestick[7] # timestamp unix
                        # number_of_trades = candlestick[8] # timestamp unix
                        # taker_buy_base_asset_volume = candlestick[9] # timestamp unix
                        # taker_buy_quote_asset_volume = candlestick[10] # timestamp unix

                        new_crypto_price = Crypto_price(crypto_id=crypto_id, date=bar_date, open=open, high=high, low=low, close=close, volume=volume, sma_20=sma_20, sma_50=sma_50, rsi_14=rsi_14)
                        db.session.add(new_crypto_price)
                        print(f"added price to {symbol}")

                    except Exception as e:
                        print(f"No stock-price added {e}")

            db.session.commit()
        print("...populated crypto prices...")

    # def test():
    #     print("Bonjour motherfucker")