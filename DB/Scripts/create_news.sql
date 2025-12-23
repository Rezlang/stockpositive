CREATE TABLE NewsArticles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    content TEXT,
    link TEXT,
    imagelink TEXT,
    keywords TEXT[],
    creator TEXT[],
    symbols TEXT[],
    pubdate TIMESTAMP,
    sourcename TEXT,
    sentiment TEXT,
    aisummary TEXT
);
