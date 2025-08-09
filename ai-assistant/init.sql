
-- Drop tables if they exist - this is done as a contingency to avert potential errors caused by wrong typecasting of columns
DROP TABLE IF EXISTS chats;
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
INSERT INTO users (username, password)
VALUES ('president', 'obama')
ON CONFLICT (username) DO NOTHING;


CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    model TEXT,
    message TEXT,
    response TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
