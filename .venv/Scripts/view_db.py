import sqlite3

# Підключення до бази даних
conn = sqlite3.connect("rental_bot.db")
cursor = conn.cursor()

# Виведення всіх користувачів
print("📋 Користувачі:")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

# Виведення всіх оренд
print("\n🚗 Оренди:")
cursor.execute("SELECT * FROM rentals")
for row in cursor.fetchall():
    print(row)

# Закриваємо з'єднання
conn.close()
