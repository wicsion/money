FROM python:3.10-slim
WORKDIR /app

# Установите переменную PORT по умолчанию
ENV PORT=8000

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Создаем директории для медиафайлов
RUN mkdir -p /app/media/avatars /app/media/properties /app/media/property_images

RUN python manage.py collectstatic --noinput

# Используйте переменную PORT
CMD ["sh", "-c", "gunicorn real_estate_portal.wsgi --bind 0.0.0.0:$PORT"]