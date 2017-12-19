web: gunicorn twitteranalyser.wsgi --log-file=-
worker: celery worker -A twitteranalyser --concurrency=1
