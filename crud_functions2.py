import sqlite3


conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL
)
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
    )
    """)

conn.commit()

cursor.execute("SELECT id, title, description, price FROM Products")
products = cursor.fetchall()

def add_user(username, email, age):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO Users (username, email, age, balance)
        VALUES (?, ?, ?, 1000)
        """, (username, email, age))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Пользователь с именем {username} уже существует.")
    finally:
        conn.close()

def is_included(username):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM Users WHERE username = ?
    """, (username,))
    result = cursor.fetchone()[0]

    conn.close()
    return result > 0

Products = [
    ('Продукт 1', 'Описание продукта 1', 100),
    ('Продукт 2', 'Описание продукта 2', 200),
    ('Продукт 3', 'Описание продукта 3', 300),
    ('Продукт 4', 'Описание продукта 4', 400),
    ]

cursor.executemany("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)", Products)
conn.commit()

def get_all_products():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, price FROM Products")
    products = cursor.fetchall()
    conn.close()
    return products

def remove_duplicates():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM Products
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM Products
        GROUP BY title, description, price
    )
    """)
    conn.commit()
    conn.close()


conn.close()
