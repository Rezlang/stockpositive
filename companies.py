from dataclasses import dataclass
from typing import List


@dataclass
class Company:
    names: List[str]
    tickers: List[str]


COMPANIES = [
    Company(
        names=["Apple", "Apple Inc", "AAPL"],
        tickers=["AAPL"]
    ),
    Company(
        names=["Microsoft", "Microsoft Corporation", "MSFT"],
        tickers=["MSFT"]
    ),
    Company(
        names=["Alphabet", "Google", "GOOGL", "GOOG"],
        tickers=["GOOGL", "GOOG"]
    ),
    Company(
        names=["Amazon", "Amazon.com", "AMZN"],
        tickers=["AMZN"]
    ),
    Company(
        names=["Nvidia", "NVIDIA", "NVDA"],
        tickers=["NVDA"]
    ),
    Company(
        names=["Meta", "Meta Platforms", "Facebook", "META"],
        tickers=["META"]
    ),
    Company(
        names=["Tesla", "TSLA"],
        tickers=["TSLA"]
    ),
    Company(
        names=["Berkshire Hathaway", "Berkshire", "BRK.A", "BRK.B"],
        tickers=["BRK.A", "BRK.B"]
    ),
    Company(
        names=["Eli Lilly", "Lilly", "LLY"],
        tickers=["LLY"]
    ),
    Company(
        names=["Broadcom", "AVGO"],
        tickers=["AVGO"]
    ),
    Company(
        names=["Costco", "Costco Wholesale", "COST"],
        tickers=["COST"]
    )
]
