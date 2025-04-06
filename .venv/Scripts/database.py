import sqlite3


def init_db():
    conn = sqlite3.connect("rental_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        phone TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        car_type TEXT,
        fuel_type TEXT,
        transmission TEXT,
        extras TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, name, phone):
    conn = sqlite3.connect("rental_bot.db")
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO users (user_id, name, phone) VALUES (?, ?, ?)", (user_id, name, phone))
    conn.commit()
    conn.close()


def add_rental(user_id, car_type, fuel_type, transmission, extras):
    conn = sqlite3.connect("rental_bot.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO rentals (user_id, car_type, fuel_type, transmission, extras) VALUES (?, ?, ?, ?, ?)",
                   (user_id, car_type, fuel_type, transmission, extras))

    conn.commit()
    conn.close()
