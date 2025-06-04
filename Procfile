release: python manage.py migrate
web: gunicorn real_estate_portal.wsgi --workers 3 --bind 0.0.0.0:$PORT
release: |
  python manage.py migrate
  python manage.py collectstatic --noinput