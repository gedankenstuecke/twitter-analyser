import celery
import os
app = celery.Celery('example')
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])


@app.task
def add(x, y):
    return x + y
