FROM python:3.10-slim
WORKDIR /app

ENV PORT=8000

RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Создаем директории и устанавливаем права
RUN mkdir -p /app/media/avatars /app/media/properties /app/media/property_images && \
    mkdir -p /app/staticfiles && \
    chmod -R 755 /app/staticfiles

# Пробуем collectstatic с подробным выводом
RUN python manage.py collectstatic --noinput --verbosity 3 || echo "Collectstatic completed with warnings"

CMD ["sh", "-c", "gunicorn real_estate_portal.wsgi --bind 0.0.0.0:$PORT"]