import requests
import time
import mysql.connector
from zoneinfo import ZoneInfo  # Python 3.9+
from datetime import datetime as dt

API_KEY   = "demo"  # <- replace with your key
INTERVAL  = "5min"
SYMBOLS   = ["IBM", "AAPL", "MSFT", "GOOGL"]
BASE_URL  = "https://www.alphavantage.co/query"

# ---- MySQL config ----
DB_CFG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",           # <- set your password
    "database": "stock_data", # <- ensure this DB exists
}

TZ_SRC = ZoneInfo("America/New_York")  # Alpha Vantage intraday timestamps
TZ_UTC = ZoneInfo("UTC")

def get_conn():
    return mysql.connector.connect(**DB_CFG)

def ensure_table():
    ddl = """
    CREATE TABLE IF NOT EXISTS stock_daily (
        timestamp  DATETIME     NOT NULL,   -- stored in UTC
        symbol     VARCHAR(16)  NOT NULL,
        open       DECIMAL(12,6),
        high       DECIMAL(12,6),
        low        DECIMAL(12,6),
        close      DECIMAL(12,6),
        volume     BIGINT,
        PRIMARY KEY (symbol, timestamp)
    ) ENGINE=InnoDB;
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(ddl)
        conn.commit()
    finally:
        cur.close()
        conn.close()

def fetch_all_stock_data(symbol: str):
    """Fetch all available intraday bars for one symbol."""
    url = (f"{BASE_URL}?function=TIME_SERIES_INTRADAY&symbol={symbol}"
           f"&interval={INTERVAL}&outputsize=full&apikey={API_KEY}")
    r = requests.get(url, timeout=30)
    data = r.json()

    # Handle API messages (rate limit, invalid symbol, etc.)
    if any(k in data for k in ("Note", "Error Message", "Information")):
        print(f"⚠️ API message for {symbol}: {data}")
        return None

    ts_key = f"Time Series ({INTERVAL})"
    ts = data.get(ts_key, {})
    if not ts:
        print(f"No time series data for {symbol}.")
        return None

    print(f"Retrieved {len(ts)} records for {symbol}")
    return ts

def to_rows(symbol: str, time_series: dict):
    """
    Convert Alpha Vantage dict → list of tuples:
    (timestamp_utc, symbol, open, high, low, close, volume)
    """
    rows = []
    for ts_str, entry in time_series.items():
        # "2025-10-03 19:55:00" is US/Eastern → convert to UTC
        local_dt = dt.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ_SRC)
        utc_dt = local_dt.astimezone(TZ_UTC).replace(tzinfo=None)  # naive UTC for MySQL DATETIME
        rows.append((
            utc_dt,
            symbol,
            float(entry["1. open"]),
            float(entry["2. high"]),
            float(entry["3. low"]),
            float(entry["4. close"]),
            int(float(entry["5. volume"])),
        ))
    # Oldest → newest is nice to have
    rows.sort(key=lambda r: r[0])
    return rows

def upsert_rows(rows):
    """Insert or update by (symbol, timestamp) PK."""
    if not rows:
        return 0
    sql = """
    INSERT INTO stock_daily
        (timestamp, symbol, open, high, low, close, volume)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        open=VALUES(open),
        high=VALUES(high),
        low=VALUES(low),
        close=VALUES(close),
        volume=VALUES(volume);
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.executemany(sql, rows)
        conn.commit()
        return cur.rowcount
    finally:
        cur.close()
        conn.close()

def main():
    ensure_table()
    for sym in SYMBOLS:
        ts = fetch_all_stock_data(sym)
        if ts:
            rows = to_rows(sym, ts)
            n = upsert_rows(rows)
            print(f"✅ Upserted {len(rows)} rows for {sym} (affected: {n})")
        # Respect free-tier rate limit (5 calls/min). 15s is safe.
        time.sleep(15)

if __name__ == "__main__":
    main()