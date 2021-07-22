class opening_breakdown(object):

    def foo():
        print('foo')

    def strategy():

        import smtplib, ssl  # E-Mail
        from website import config
        from website.helpers import helpers
        from website.models import Param_stock_strategy_breakdown, Stock_strategy, Strategy, Stock, Market
        from website.extensions import db, alpaca_api
        from sqlalchemy import asc
        import pandas as pd
        import time
        t0= time.time()

        DEBUG = False

        ## TODO:
        # - Database for opening-times Market and times to apply the strategy.
        # - Backtesting strategy with UI

        # current_date = '2021-03-12'                                                                       # Check on specific day (DEBUG)
        current_date = helpers.get_date_today()                                                             # Check today (Script)
        current_time = pd.Timestamp.today().strftime("%H:%M")                                                         # Check today (Script)
        if DEBUG == True: print(f"Current date: {current_date}")

        context = ssl.create_default_context()                                                              # Email
        messages = []                                                                                       # Placeholder messages

        # [cursor, connection] = helpers.init_database()                                                      # Init Database

        strategy_id = db.session.query(
            Strategy
        ).with_entities(
            Strategy.id,
        ).filter(
            Strategy.name == 'opening_range_breakdown'
        ).first()[0]
        
        # # Get Stocks which get handled with opening range breakout strategy

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
                Param_stock_strategy_breakdown,
                Param_stock_strategy_breakdown.parameter_id == Stock_strategy.parameter_id
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

                Param_stock_strategy_breakdown.observe_from,
                Param_stock_strategy_breakdown.observe_until,
                Param_stock_strategy_breakdown.trade_price
            ).filter(
                Stock_strategy.strategy_id == strategy_id
        #         where stock_strategy.strategy_id = ?
            ).order_by(
                asc(
                    Stock.symbol
                )
            ).all()

        symbols = [stock.symbol for stock in stocks]                                                     # extract symbols from stocks                   (stock)

        for stock in stocks:
            if DEBUG == True: print(stock.name)

        for symbol in symbols:
            if DEBUG == True: print(symbol)

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
            
            pre_end = end_time - pd.Timedelta("15min")
            if DEBUG == True: print("Ready_steady")                                                             # end-date and time market-closing
            if current_time < pre_end.strftime("%H:%M"):                                                          # if market is open
                if DEBUG == True: print("go breakdown")
                    
                observe_from_bar = helpers.get_timestamp(
                    current_date, stock.observe_from,
                    stock.timezone).isoformat()                                                              # begin opening range breakdown when market opens
                observe_until_bar = helpers.get_timestamp(
                    current_date, stock.observe_until,
                    stock.timezone).isoformat()                                                              # ends at determinded time

                time_bars = alpaca_api.get_barset(
                    stock.symbol, 'minute', start=start,
                    end=end).df                                                                                 # get stock-specific minute bars for the day online
                # minute_bars = alpaca_api.polygon.historic_agg_v2(stock.symbol, 1, 'minute', _from='2020-10-28', to='2020-10-29').df

                # if DEBUG == True: print(time_bars)
                # if DEBUG == True: print(observe_until_bar)
                # if DEBUG == True: print(helpers.get_timestamp2(f"{time_bars[stock.symbol].index[0]}", stock.timezone).isoformat())
                
                opening_range_mask = [
                    (helpers.get_timestamp2(f"{index}", stock.timezone).isoformat() >= observe_from_bar) &   # look if actual time before (opening range)
                    (helpers.get_timestamp2(f"{index}", stock.timezone).isoformat() < observe_until_bar)     # loof if actual time after (opening range)
                    for index in time_bars[stock.symbol].index]                                              # in every entry of the bars

                opening_range_bars = time_bars.loc[opening_range_mask]                                          # select bars which are in the opening range
                if DEBUG == True: print(opening_range_bars)

                opening_range_low = opening_range_bars[stock.symbol]['low'].min()                            # lower range of opening bars
                opening_range_high = opening_range_bars[stock.symbol]['high'].max()                          # upper range of opening bars
                opening_range = opening_range_high - opening_range_low                                          # calculate opening range from upper and lower
                if DEBUG == True: print(opening_range)

                after_opening_range_mask = time_bars.index >= observe_until_bar                                 # look if actual time is out of opening range
                after_opening_range_bars = time_bars.loc[after_opening_range_mask]                              # select bars which are out of the opening range
                if DEBUG == True: print(after_opening_range_bars)

                after_opening_range_breakdown = after_opening_range_bars[
                    after_opening_range_bars[stock.symbol]['close'] < opening_range_low]                     # check whether bar closed below lower opening range
                if DEBUG == True: print(after_opening_range_breakdown)

                if not after_opening_range_breakdown.empty:                                                     # if a stock closed below lower opening range, sell
                    if not stock.symbol not in existing_order_symbols:                                           # if the stock has not been traded yet
                        limit_price = after_opening_range_breakdown.iloc[0][stock['symbol']]['close']           # determine stop price
                        message = f"selling short for {stock.symbol}  {stock.name}, closed below {opening_range_low}\n\n{after_opening_range_breakdown.iloc[0][stock.symbol]}\n\n"
                        if DEBUG == True: print(message)
                        f = open("logfiles/opening_range_breakdown.txt", "a")
                        f.write(message + "\r")
                        f.close()
                        messages.append(message)

                        try:
                            alpaca_api.submit_order(
                                symbol=stock.symbol,
                                side='sell',
                                qty=helpers.calculate_quantity(stock.trade_price, limit_price),
                                time_in_force='day',
                                type='trailing_stop',
                                trail_percent='0.70'
                            )
                        except Exception as e:
                            print(f"could not submit order {e}")
                    else:
                        if current_time > pre_end.strftime("%H:%M") and current_time < end_time.strftime("%H:%M"):
                            response = alpaca_api.close_position(stock.symbol)
                            print(response)
                        else:
                            print(f"Already an order for {stock.symbol}, skipping")

            if DEBUG == True: print(messages)

            if len(messages) > 0:
                with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
                    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

                    email_message = f"Subject: Trade Notification for {current_date}\n\n"
                    email_message += "\n\n".join(messages)

                    server.sendmail(config.EMAIL_ADDRESS, 'kim.schenk@hotmail.com', email_message)
        t1 = time.time() - t0
        print("Time elapsed breakdown: ", t1) # CPU seconds elapsed (floating point)
