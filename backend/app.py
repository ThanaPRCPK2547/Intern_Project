import requests
import datetime
import time
import csv

API_KEY = "demo"  # Replace with your own Alpha Vantage API key
INTERVAL = "5min"
SYMBOLS = ["IBM", "AAPL", "MSFT", "GOOGL"]  # 👈 Add as many as you like

BASE_URL = "https://www.alphavantage.co/query"

def fetch_all_stock_data(symbol):
    """Fetches all intraday stock data for one symbol."""
    url = f"{BASE_URL}?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={INTERVAL}&outputsize=full&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Handle API limit or error messages
        if "Note" in data or "Error Message" in data:
            print(f"⚠️ API message for {symbol}: {data}")
            return None
        
        time_series = data.get(f"Time Series ({INTERVAL})", {})
        if not time_series:
            print(f"No time series data for {symbol}.")
            return None
        
        print(f"\n[{datetime.datetime.now()}] Retrieved {len(time_series)} records for {symbol}")
        return time_series

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def save_to_csv(symbol, time_series):
    """Saves one symbol’s data to its own CSV file."""
    filename = f"{symbol}_intraday.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for ts, entry in sorted(time_series.items()):
            writer.writerow([
                ts,
                entry["1. open"],
                entry["2. high"],
                entry["3. low"],
                entry["4. close"],
                entry["5. volume"]
            ])
    print(f"✅ Saved data for {symbol} to {filename}")


# --- MAIN LOOP ---
for symbol in SYMBOLS:
    data = fetch_all_stock_data(symbol)
    if data:
        save_to_csv(symbol, data)
    # Avoid hitting free-tier rate limit (5 calls/min)
    time.sleep(15)  # ⏱ wait 15s between requests is safer