CREATE TABLE oauth_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    oauth_name VARCHAR(100) NOT NULL,
    access_token VARCHAR(1024) NOT NULL,
    expires_at INTEGER,
    refresh_token VARCHAR(1024),
    account_id VARCHAR(320) NOT NULL,
    account_email VARCHAR(320),
    CONSTRAINT fk_oauth_accounts_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT unique_oauth_account UNIQUE (oauth_name, account_id)
);

CREATE INDEX idx_oauth_accounts_user_id ON oauth_accounts(user_id);
CREATE INDEX idx_oauth_accounts_oauth_name ON oauth_accounts(oauth_name);