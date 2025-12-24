INSERT INTO users (
    usergroup_id,
    username,
    email,
    phone_number,
    hashed_password
)
VALUES
(
    (SELECT id FROM usergroups WHERE name = 'admin'),
    'testuser',
    'test@test.com',
    '1234567890',
    '$2b$12$g8FSRzt.Q47ZOH4bUvnoCeZ4KOWU.LfwbGiPecI8fhvu86w4NJelS'
),
(
    (SELECT id FROM usergroups WHERE name = 'user'),
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