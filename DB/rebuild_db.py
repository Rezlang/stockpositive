import psycopg2
import os

DB_NAME = "stockpositive"
DB_USER = "postgres"
DB_PASSWORD = "app"
DB_HOST = "localhost"
DB_PORT = "5432"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")
INSERT_DIR = os.path.join(BASE_DIR, "Insert")
ORDER_FILE = os.path.join(BASE_DIR, "order.txt")


def read_sql_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def execute_sql_files(conn, folder, ordered_files):
    with conn.cursor() as cur:
        for filename in ordered_files:
            file_path = os.path.join(folder, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Missing SQL file: {file_path}")

            print(f"Executing {file_path}")
            sql = read_sql_file(file_path)
            cur.execute(sql)
    conn.commit()


def recreate_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{DB_NAME}'
              AND pid <> pg_backend_pid();
        """)

        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
        cur.execute(f"CREATE DATABASE {DB_NAME};")

    conn.close()
    print(f"Database '{DB_NAME}' recreated")


def main():
    with open(ORDER_FILE, "r", encoding="utf-8") as f:
        ordered_files = [line.strip() for line in f if line.strip()]

    recreate_database()

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    print("Running CREATE scripts")
    execute_sql_files(conn, SCRIPTS_DIR, ordered_files)

    print("Running INSERT scripts")
    execute_sql_files(conn, INSERT_DIR, ordered_files)

    conn.close()
    print("Database rebuild complete")


if __name__ == "__main__":
    main()
