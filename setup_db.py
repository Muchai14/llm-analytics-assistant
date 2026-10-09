import sqlite3

conn = sqlite3.connect('demo.db')

conn.execute('''CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER,
    customer_id INTEGER,
    product TEXT,
    amount REAL,
    order_date TEXT
)''')

conn.execute("DELETE FROM orders")

conn.execute("INSERT INTO orders VALUES (1, 101, 'Laptop', 1200, '2026-01-15')")
conn.execute("INSERT INTO orders VALUES (2, 102, 'Phone', 800, '2026-02-20')")
conn.execute("INSERT INTO orders VALUES (3, 101, 'Tablet', 600, '2026-03-10')")
conn.execute("INSERT INTO orders VALUES (4, 103, 'Laptop', 1200, '2026-03-15')")
conn.execute("INSERT INTO orders VALUES (5, 102, 'Phone', 800, '2026-04-01')")

conn.commit()
conn.close()

print("Database created: demo.db")
