web: gunicorn twitteranalyser.wsgi --log-file=-
worker: celery -A twitteranalyser worker --concurrency=1
