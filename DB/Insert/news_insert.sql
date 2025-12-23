INSERT INTO news_articles (
    title,
    description,
    content,
    link,
    imagelink,
    keywords,
    creator,
    symbol,
    pubdate,
    sourcename,
    sentiment,
    aisummary
) VALUES
(
    'Test Article 1',
    'This is the description of test article 1.',
    'Full content of test article 1 goes here.',
    'https://example.com/article1',
    'https://example.com/image1.jpg',
    'test,news,article1',
    'Author One',
    'AAPL',
    '2025-12-21 10:00:00',
    'ExampleSource',
    '0.75',
    'AI summary for test article 1.'
),
(
    'Test Article 2',
    'This is the description of test article 2.',
    'Full content of test article 2 goes here.',
    'https://example.com/article2',
    'https://example.com/image2.jpg',
    'test,news,article2',
    'Author Two',
    'GOOG',
    '2025-12-21 11:00:00',
    'ExampleSource',
    '-0.2',
    'AI summary for test article 2.'
);
