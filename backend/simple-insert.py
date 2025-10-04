import mysql.connector

# --- Connect to your MySQL database ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="stock_data"
)
cursor = db.cursor()

# --- Manual variables (you can change these) ---
timestamp = "2025-10-03 19:55:00"
symbol = "IBM"
open_price = 288.39
high_price = 288.75
low_price = 288.39
close_price = 288.45
volumne = 93

# --- Insert into MySQL ---
sql = """INSERT INTO stock_daily (timestamp, symbol, open, high, low, close, volumne)
         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
val = (timestamp, symbol, open_price, high_price, low_price, close_price, volumne)
cursor.execute(sql, val)
db.commit()

print("✅ 1 record inserted successfully!")

cursor.close()
db.close()