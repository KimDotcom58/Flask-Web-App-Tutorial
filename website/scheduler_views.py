from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import asc
from .extensions import db


scheduler_views = Blueprint('scheduler_views', __name__)

@scheduler_views.route('/', methods=['GET', 'POST'])
@login_required
def scheduler():

    from .models import Strategy, Trading

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
        ).with_entities(
            Trading.trading,
            Trading.id
        ).order_by(
            asc(Trading.id)
        ).all()

    for trade in trading:
        print(trade.trading)

    return render_template("scheduler.html", user=current_user, strategies=strategies, trading=trading)