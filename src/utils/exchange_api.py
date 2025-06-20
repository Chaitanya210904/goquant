import requests

def fetch_symbols(exchange):
    exchange = exchange.lower()
    try:
        if exchange == "binance":
            url = "https://api.binance.com/api/v3/exchangeInfo"
            response = requests.get(url)
            return [s["symbol"] for s in response.json().get("symbols", [])]

        elif exchange == "bybit":
            url = "https://api.bybit.com/v5/market/instruments-info?category=spot"
            response = requests.get(url)
            return [s["symbol"] for s in response.json()["result"].get("list", [])]

        elif exchange == "okx":
            url = "https://www.okx.com/api/v5/public/instruments?instType=SPOT"
            response = requests.get(url)
            return [s["instId"] for s in response.json().get("data", [])]

        elif exchange == "deribit":
            url = "https://www.deribit.com/api/v2/public/get_instruments?currency=BTC&kind=spot"
            response = requests.get(url)
            return [s["instrument_name"] for s in response.json().get("result", [])]

        else:
            raise ValueError("Exchange not supported")

    except Exception as e:
        print(f"Error fetching symbols for {exchange}: {e}")
        return []

def fetch_price(exchange, symbol):
    exchange = exchange.lower()
    try:
        if exchange == "binance":
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            return response.json().get("price", "Unavailable")

        elif exchange == "bybit":
            url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
            response = requests.get(url)
            return response.json()["result"]["list"][0].get("lastPrice", "Unavailable")

        elif exchange == "okx":
            url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
            response = requests.get(url)
            return response.json()["data"][0].get("last", "Unavailable")

        elif exchange == "deribit":
            url = f"https://www.deribit.com/api/v2/public/ticker?instrument_name={symbol}"
            response = requests.get(url)
            return response.json()["result"].get("last_price", "Unavailable")

        else:
            raise ValueError("Exchange not supported")

    except Exception as e:
        print(f"Error fetching price for {exchange} {symbol}: {e}")
        return "Unavailable"
