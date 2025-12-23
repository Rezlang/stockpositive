import requests
from typing import List, Optional
import sys
import json
import pandas as pd


def print_get_response(response):
    if response == []:
        print("no matching news")
        return
    rows = []
    for article in response:
        rows.append({
            'symbol': article['symbol'],
            'title': article['title'],
            'source': article['sourcename'],
            'pubdate': article['pubdate'],
            'link': article['link'],
            'id': article['id']
        })

    df = pd.DataFrame(rows)

    print("\n=== response ===")
    print(df[['symbol', 'title', 'source']].to_string(index=False))


def load_news(source: str = "market", symbols: Optional[List[str]] = None):
    url = "http://127.0.0.1:8000/news/load-news"
    params = {"source": source}

    if symbols:
        params["symbols"] = ",".join(symbols)

    response = requests.get(url, params=params)
    return response


def getNews(feedId):
    url = "http://127.0.0.1:8000/news/get-news"
    params = {"feedId": feedId}

    response = requests.get(url, params=params)
    return response


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py [load|get] [args...]")
        print("  load: python script.py load [symbol1 symbol2 ...]")
        print("  get: python script.py get [feedId]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "load":
        symbols = sys.argv[2:] if len(sys.argv) > 2 else ["AAPL", "MSFT"]
        response = load_news(symbols=symbols)
        print(response.status_code)
        print(response.json())
    elif command == "get":
        feedId = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        response = getNews(feedId).json()
        print_get_response(response)
    else:
        print(f"Unknown command: {command}")
        print("Use 'load' or 'get'")
        sys.exit(1)


if __name__ == "__main__":
    main()
