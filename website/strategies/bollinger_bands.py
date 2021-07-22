class bollinger_bands(object):

    def foo():
        print('foo')

    def strategy():
        
        import smtplib, ssl  # E-Mail
        from website import config
        from website.helpers import helpers
        from website.models import Param_stock_strategy_bollinger, Stock_strategy, Strategy, Stock, Market
        from website.extensions import db, alpaca_api
        from sqlalchemy import asc
        import tulipy
        import pandas as pd
        import time
        t0= time.time()

        DEBUG = False

        ## TODO:
        # - Database for opening-times Market and times to apply the strategy.
        # - Backtesting strategy with UI

        current_date = '2021-06-24'                                                                       # Check on specific day (DEBUG)
        # current_date = helpers.get_date_today()                                                             # Check today (Script)
        if DEBUG == True: print(f"Current date: {current_date}")

        context = ssl.create_default_context()                                                              # Email
        messages = []                                                                                       # Placeholder messages

        # [cursor, connection] = helpers.init_database()                                                      # Init Database

        strategy_id = db.session.query(
            Strategy
        ).with_entities(
            Strategy.id,
        ).filter(
            Strategy.name == 'bollinger_bands'
        ).first()[0]
        
        # Get Stocks which get handled with bollinger band strategy

        stocks = db.session.query(
                Stock
            ).join(
                Market,
                Market.id == Stock.market_id
        #         join market on market.id = stock.market_id
            ).join(
                Stock_strategy, 
                Stock_strategy.stock_id == Stock.id
        #         join stock_strategy on stock_strategy.stock_id = stock.id
            ).join(
                Param_stock_strategy_bollinger,
                Param_stock_strategy_bollinger.parameter_id == Stock_strategy.parameter_id
        #         join param_stock_strategy_breakdown on param_stock_strategy_breakdown.id = stock_strategy.parameter_id
            ).with_entities(
        #         select stock.symbol, stock.name, market.market_open_local, market.market_close_local,
        #             market.timezone, param_stock_strategy_breakdown.observe_from,
        #             param_stock_strategy_breakdown.observe_until,
        #             param_stock_strategy_breakdown.trade_price
                Stock.symbol, 
                Stock.name,

                Market.market_open_local, 
                Market.market_close_local, 
                Market.timezone, 

                Param_stock_strategy_bollinger.period,
                Param_stock_strategy_bollinger.stddev,
                Param_stock_strategy_bollinger.trade_price
            ).filter(
                Stock_strategy.strategy_id == strategy_id
        #         where stock_strategy.strategy_id = ?
            ).order_by(
                asc(
                    Stock.symbol
                )
            ).all()

        # symbols = [stock.symbol for stock in stocks]                                                     # extract symbols from stocks                   (stock)

        # for stock in stocks:
            # if DEBUG == True: print(stock.name)

        # for symbol in symbols:
            # if DEBUG == True: print(symbol)

        # orders = alpaca_api.list_orders()                                                                            # get list of all orders
        orders = alpaca_api.list_orders(status='all', after=current_date)                                        # get list of all orders from today (we only want to trade once a day)
        existing_order_symbols = [
            order.symbol for order in orders if order.status !=
            'canceled'  # if any order not been placed, trade it        (List)
        ]

        for stock in stocks:
            start = helpers.get_timestamp(
                current_date, stock.market_open_local,
                stock.timezone).isoformat()                                                              # start-date and time market-opening
            end_time = helpers.get_timestamp(
                current_date, stock.market_close_local,
                stock.timezone)     
            end = end_time.isoformat()                                                         # end-date and time market-closing
            
            if DEBUG == True: print("Ready_steady")                                                             # end-date and time market-closing
            if not pd.Timestamp.today().strftime("%H:%M") < end_time.strftime("%H:%M"):                                                          # if market is open
                if DEBUG == True: print("go bollinger")                                                           # end-date and time market-closing

                time_bars = alpaca_api.get_barset(
                    stock.symbol, 'minute', start=start,
                    end=end).df                                                                                 # get stock-specific minute bars for the day online
                # minute_bars = alpaca_api.polygon.historic_agg_v2(stock['symbol'], 1, 'minute', _from='2020-10-28', to='2020-10-29').df

                if DEBUG == True: print(time_bars)
                if DEBUG == True: print(start)
                # if DEBUG == True: print(helpers.get_timestamp2(f"{time_bars[stock.symbol].index[0]}", stock.timezone).isoformat())
                
                market_open_mask = [
                    (helpers.get_timestamp2(f"{index}", stock.timezone).isoformat() >= start) &
                    (helpers.get_timestamp2(f"{index}", stock.timezone).isoformat() < end)
                    for index in time_bars[stock.symbol].index
                ]

                market_open_bars = time_bars[stock.symbol].loc[market_open_mask]

                if len(market_open_bars) >= 20:
                    closes = market_open_bars.close.values

                    lower, middle, upper = tulipy.bbands(closes, stock.period, stock.stddev)
                    current_candle = market_open_bars.iloc[-1]
                    previous_candle = market_open_bars.iloc[-2]

                    if current_candle.close > lower[-1] and previous_candle.close < lower[-2]:
                        print(f"{stock.symbol} closed below the lower bollingerband")

                        if stock.symbol not in existing_order_symbols:
                            limit_price = current_candle.close

                            candle_range = previous_candle.high - previous_candle.low
                            message = f"placing order for {stock.symbol} at {limit_price}"
                            if DEBUG == True: print(message)
                            f = open("logfiles/bollinger_bands.txt", "a")
                            f.write(message + "\r")
                            f.close()
                            messages.append(message)

                            try:
                                alpaca_api.submit_order(
                                    symbol=stock.symbol,
                                    side='buy',
                                    type='limit',
                                    qty=helpers.calculate_quantity(stock.trade_price, limit_price),
                                    time_in_force='day',
                                    order_class='bracket',
                                    limit_price=limit_price,
                                    take_profit=dict(
                                        limit_price=limit_price + candle_range * 3,
                                    ),
                                    stop_loss=dict(
                                        stop_price=previous_candle.low,
                                    )
                                )
                            except Exception as e:
                                print(f"could not submit order {e}")
                        else:
                            print(f"Already an order for {stock.symbol}, skipping")

            # print(messages)

            if len(messages) > 0:
                with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
                    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

                    email_message = f"Subject: Trade Notification for {current_date}\n\n"
                    email_message += "\n\n".join(messages)

                    server.sendmail(config.EMAIL_ADDRESS, 'kim.schenk@hotmail.com', email_message)

        t1 = time.time() - t0
        print("Time elapsed bollinger: ", t1) # CPU seconds elapsed (floating point)

    def daily_close():
        from website.extensions import alpaca_api
        response = alpaca_api.close_all_positions()
        response = alpaca_api.close_position()
        print(response)

