from . import scheduler

class scheduled_tasks(object):

    # interval example
    @scheduler.task('interval', id='do_job_1', seconds=1, misfire_grace_time=900)
    def job1():
        # with scheduler.app.app_context():
        #     from .database import database
        #     database.populate_stocks()
        #     database.populate_stock_prices()
            print('Job 1 executed')

    # cron examples
    @scheduler.task('interval', id='do_job_2', seconds=5, misfire_grace_time=900)
    def job2():
        print('Job 2 executed')

    @scheduler.task('interval', id='do_job_3', seconds=10, misfire_grace_time=900)
    def job3():
        print('Job 3 executed')