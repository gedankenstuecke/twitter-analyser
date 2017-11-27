web: gunicorn twitteranalyser.wsgi --log-file=-
worker: celery worker --app=tasks.app
