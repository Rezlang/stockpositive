INSERT INTO userfeeds (user_id, feedname, stocks, sources)
VALUES
(1, 'Tech Stocks', ARRAY['AAPL','GOOG','MSFT'], ARRAY['finance.yahoo.com','bloomberg.com']),
(2, 'Energy Stocks', ARRAY['XOM','CVX'], ARRAY['reuters.com','cnbc.com']),
(3, 'Crypto Watch', ARRAY['BTC','ETH'], ARRAY['coinmarketcap.com','binance.com']),
(1, 'Healthcare Stocks', ARRAY['PFE','JNJ'], ARRAY['finance.yahoo.com','fool.com']),
(2, 'Automotive Stocks', ARRAY['TSLA','GM','F'], ARRAY['bloomberg.com','cnbc.com']),
(3, 'Global Indexes', ARRAY['S&P 500','NASDAQ','DOW'], ARRAY['reuters.com','investing.com']);
