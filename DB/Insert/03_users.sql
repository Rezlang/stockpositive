INSERT INTO users (
    usergroup_id,
    username,
    email,
    phone_number,
    hashed_password
)
VALUES
(
    (SELECT id FROM usergroups WHERE name = 'user'),
    'testuser',
    'test@example.com',
    '1234567890',
    '$2b$12$u8TUnD0vhJERde8CbK9ZXu3ohQKSuxMCFMsHFKraOHtXtrzBqOLU6'
),
(
    (SELECT id FROM usergroups WHERE name = 'admin'),
    'adminuser',
    'admin@example.com',
    '1112223333',
    '$2b$12$adminhashedpasswordexample'
),
(
    (SELECT id FROM usergroups WHERE name = 'free'),
    'freeuser',
    'free@example.com',
    '9998887777',
    '$2b$12$freehashedpasswordexample'
);