FROM python:3.10-slim
WORKDIR /app

# Установите переменную PORT по умолчанию
ENV PORT=8000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput

# Используйте переменную PORT
CMD ["sh", "-c", "gunicorn real_estate_portal.wsgi --bind 0.0.0.0:$PORT"]