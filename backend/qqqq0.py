import requests
import pandas as pd

def fetch_monthly_data(symbol: str, api_key: str):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_MONTHLY",
        "symbol": symbol,
        "apikey": api_key,
        # optionally: "datatype": "csv"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    # The monthly time series is under key "Monthly Time Series"
    if "Monthly Time Series" not in data:
        raise ValueError("Unexpected response format or error: " + str(data))
    ts = data["Monthly Time Series"]
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(ts, orient="index")
    # Rename columns for convenience
    df = df.rename(
        columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume",
        }
    )
    # Convert index to datetime, and convert values to numeric types
    df.index = pd.to_datetime(df.index)
    df = df.apply(pd.to_numeric)
    # Optional: sort by date ascending
    df = df.sort_index()
    return df

if __name__ == "__main__":
    symbol = "IBM"
    api_key = "demo"  # replace with your own key
    df = fetch_monthly_data(symbol, api_key)
    print(df.head())
    print(df.tail())