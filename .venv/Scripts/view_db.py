import sqlite3


def view_database(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Отримуємо список таблиць у базі даних
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("У базі даних немає таблиць.")
            return

        print("Доступні таблиці:")
        for idx, table in enumerate(tables):
            print(f"{idx + 1}. {table[0]}")

        table_name = input("Введіть назву таблиці для перегляду: ")

        # Вивід даних з вибраної таблиці
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            print("Таблиця порожня.")
        else:
            for row in rows:
                print(row)

        conn.close()
    except sqlite3.Error as e:
        print(f"Помилка при доступі до бази даних: {e}")


if __name__ == "__main__":
    db_path = input("Введіть шлях до файлу бази даних (наприклад, 'bot_database.db'): ")
    view_database(db_path)