FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Сборка статики
RUN python manage.py collectstatic --noinput

# Запуск сервера
CMD ["gunicorn", "real_estate_portal.wsgi", "--bind", "0.0.0.0:$PORT"]