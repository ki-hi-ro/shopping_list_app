import os, time, psycopg2

host = os.getenv("DB_HOST", "db")
db   = os.getenv("DB_NAME", "shopping")
user = os.getenv("DB_USER", "shopping")
pwd  = os.getenv("DB_PASSWORD", "shopping")
port = int(os.getenv("DB_PORT", "5432"))

for i in range(60):
    try:
        conn = psycopg2.connect(host=host, dbname=db, user=user, password=pwd, port=port)
        conn.close()
        print("DB is ready.")
        break
    except Exception as e:
        print(f"Waiting for DB... ({i+1}/60) {e}")
        time.sleep(1)
else:
    raise SystemExit("DB is not ready, abort.")