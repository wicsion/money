FROM python:3.10-slim
WORKDIR /app

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/media /app/static
RUN chmod -R 755 /app/media

# Собираем статику
RUN python manage.py collectstatic --noinput --clear

CMD ["sh", "-c", "gunicorn real_estate_portal.wsgi --bind 0.0.0.0:$PORT"]