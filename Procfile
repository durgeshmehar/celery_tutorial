web: python manage.py migrate && gunicorn a_core.wsgi
worker: celery -A a_core worker --loglevel=info