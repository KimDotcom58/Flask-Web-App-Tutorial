from website import config
import alpaca_trade_api as tradeapi
from website.models import Stock, Market
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

stocks=Stock.query.all()
symbols = [stock.symbol for stock in stocks]

api = tradeapi.REST(config.API_KEY_ALPACA,
                    config.API_SECRET_ALPACA,
                    base_url=config.API_URL_ALPACA)

assets = api.list_assets()

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
