from twelvedata import TDClient
import os
from dotenv import load_dotenv

load_dotenv()


class twelveDataService():
    def __init__(self):
        KEY = os.getenv("TWELVEDATA_KEY")
        self.td = TDClient(apikey=KEY)

    def formatData(self, data, format="JSON"):
        if format.upper() == "CSV":
            return data.as_csv()
        elif format.upper() == "JSON":
            return data.as_json()

    def timeSeries(self, symbol, interval, outputsize, format="JSON"):
        ts = self.td.time_series(
            symbol=symbol,
            interval=interval,
            outputsize=outputsize
        )
        return self.formatData(ts, format)

    def latestPrice(self, symbol, format="JSON"):
        lp = self.td.price(symbol=symbol)
        return self.formatData(lp, format)


def main():
    td = twelveDataService()
    lp = td.latestPrice("AAPL")
    print(lp)


if __name__ == "__main__":
    main()
