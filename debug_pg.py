import psycopg2
import psycopg2.extensions

try:
    conn = psycopg2.connect(
        dbname="winwin_ocfj",
        user="winwin_ocfj_user",
        password=b"qpfjV1wtFozPvliLsXvNivhn6SFnamkT".decode("utf-8", errors="replace"),
        host="dpg-d15ji1be5dus739oisq0-a",
        port="5432"
    )
    print("✅ Успешно подключено к БД!")
except Exception as e:
    print("❌ Ошибка:", e)
