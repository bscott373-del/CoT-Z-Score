"""
Pulls daily commodity futures closing prices via yfinance and writes them to
prices.json in the repo root. Run automatically by
.github/workflows/update-prices.yml on a schedule — the static site (index.html)
just fetches this JSON file directly (same-origin, no CORS issues at all).
"""

import json
from datetime import datetime, timezone

import yfinance as yf

# Standard continuous front-month futures tickers on Yahoo Finance.
TICKERS = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Corn": "ZC=F",
    "Wheat": "ZW=F",
    "Soybeans": "ZS=F",
}


def fetch_one(name, ticker):
    hist = yf.Ticker(ticker).history(period="4y", interval="1d")
    series = {}
    for idx, row in hist.iterrows():
        close = row["Close"]
        if close == close:  # filters out NaN
            series[idx.strftime("%Y-%m-%d")] = round(float(close), 4)
    return series


def main():
    result = {}
    for name, ticker in TICKERS.items():
        try:
            series = fetch_one(name, ticker)
            result[name] = series
            print(f"{name} ({ticker}): {len(series)} daily closes")
        except Exception as err:
            print(f"FAILED {name} ({ticker}): {err}")
            result[name] = {}

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "data": result,
    }
    with open("prices.json", "w") as f:
        json.dump(output, f)
    print("Wrote prices.json")


if __name__ == "__main__":
    main()
