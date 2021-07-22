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

        symbols_xtb = xtb_api.get_all_symbols()

        category_names = []
        for symbol in symbols_xtb:
            try:
                asset_category = symbol['categoryName']
                asset_symbol = symbol['symbol']
                if asset_category not in category_names:
                    category_names.append(asset_category)
                    new_trading = Trading(trading = asset_category)
                    db.session.add(new_trading)
                    db.session.commit()
            except Exception as e:
                print(asset_symbol)
                print(e)
        print(category_names)
        print("populated tradings")

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


    def populate_markets():
        from .models import Market
        from .extensions import db

        markets=Market.query.limit(100).all()
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
                    new_market = Market(exchange=new_market[0], name=new_market[1], market_open_local=new_market[2], market_close_local=new_market[3], timezone=new_market[4], pause_start=new_market[5], pause_stop=new_market[6])
                    print(new_market.name)
                    db.session.add(new_market)
                    db.session.commit()           
                except Exception as e:
                    print(new_market[0])
                    print(e)
            else:
                print(f"Already existing, skipped {new_market[0]}")

        print("...populated markets...")


    def populate_stocks():
        from website import config
        from .models import Stock, Market, Symbol_XTB, Trading
        from .extensions import db, xtb_api, alpaca_api

        stocks=Stock.query.all()
        symbols = [stock.symbol for stock in stocks]

        assets = alpaca_api.list_assets()

        for asset in assets:
            print(asset.symbol)
            try:
                if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
                    market_id = Market.query.filter_by(exchange=asset.exchange).first().id
                    # print(market_id)
                    # print(f"Added a new stock: {asset.exchange} {asset.symbol} {asset.name}")
                    new_stock = Stock(symbol=asset.symbol, name=asset.name, market_id=market_id, shortable=asset.shortable)
                    db.session.add(new_stock)
                    db.session.commit()
            except Exception as e:
                print(asset.symbol)
                print(e)

    # CHECK IF MARKET IS OPEN FOR EURUSD
        symbols_xtb = xtb_api.get_all_symbols()

        for symbol in symbols_xtb:
            asset_symbol = symbol['symbol']

            try:
                asset_category = symbol['categoryName']

                trading_id = db.session.query(
                        Trading
                    ).filter(
                        Trading.trading == asset_category
                    ).first()

                asset_description = symbol['description']
                asset_currency = symbol['currency']
                asset_trailing_en = symbol['trailingEnabled']
                
                new_symbol = Symbol_XTB(symbol=asset_symbol, trading_id = trading_id.id, description=asset_description, currency=asset_currency, trailing_enabled = asset_trailing_en)
                db.session.add(new_symbol)
                db.session.commit()

            except Exception as e:
                print(asset_symbol)
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
        
        print("...populated stocks...")


    def populate_stock_prices():

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
                recent_closes = [bar.c for bar in barsets[symbol]]
                stock_id = stock_dict[symbol]
                print(symbol)
                date = db.session.query(func.max(Stock_price.date)).filter(Stock_price.stock_id==stock_id).scalar()

                try:
                    max_date = datetime.strptime(date, '%Y-%m-%d').date().isoformat()
                except Exception as e:
                    # print(f"No data {e}")
                    max_date = datetime.strptime('2000-01-01', '%Y-%m-%d').date().isoformat()

                for bar in barsets[symbol]:
                    bar_date = bar.t.date().isoformat()

                    if bar_date > max_date and bar_date < current_date:

                        if len(recent_closes) >= 50:
                            sma_20 = tulipy.sma(numpy.array(recent_closes), period=20)[-1]
                            sma_50 = tulipy.sma(numpy.array(recent_closes), period=50)[-1]
                            rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14)[-1]
                        else:
                            sma_20, sma_50, rsi_14 = None, None, None
                            
                        try:
                            new_stock_price = Stock_price(stock_id=stock_id, date=bar.t.date(), open=bar.o, high=bar.h, low=bar.l, close=bar.c, volume=bar.v, sma_20=sma_20, sma_50=sma_50, rsi_14=rsi_14)
                            db.session.add(new_stock_price)
                            # print(f"added price to {symbol}")

                        except Exception as e:
                            print(f"No stock-price added: {e}")

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


    def test():
        print("Bonjour motherfucker")