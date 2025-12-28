INSERT INTO userfeeds (user_id, feedname, stocks, sources)
VALUES 
(1, 'Tech Stocks', ARRAY['AAPL','GOOG','MSFT'], ARRAY['ExampleSource1','ExampleSource2']),
(2, 'Energy Stocks', ARRAY['XOM','CVX'], ARRAY['Reuters','CNBC']),
(3, 'Crypto Watch', ARRAY['BTC','ETH'], ARRAY['CoinMarketCap','Binance']),
(1, 'Healthcare Stocks', ARRAY['PFE','JNJ'], ARRAY['Yahoo Finance','Fool.com']),
(2, 'Automotive Stocks', ARRAY['TSLA','GM','F'], ARRAY['Bloomberg','CNBC']),
(3, 'Global Indexes', ARRAY['S&P 500','NASDAQ','DOW'], ARRAY['Reuters','Investing.com']);
