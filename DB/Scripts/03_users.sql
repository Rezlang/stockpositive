CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    usergroup_id INTEGER NOT NULL,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    hashed_password VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_users_usergroup
        FOREIGN KEY (usergroup_id)
        REFERENCES usergroups(id)
        ON DELETE RESTRICT
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);