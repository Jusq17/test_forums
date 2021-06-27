
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    s_word TEXT,
    admin_rights INT 
);

CREATE TABLE forums (
    id SERIAL PRIMARY KEY,
    subject TEXT,
    username TEXT,
    sent_at TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    username TEXT,
    sent_at TIMESTAMP,
    forum_id INT
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT,
    message_id INT,
    forum_id INT,
    username TEXT,
    sent_at TIMESTAMP
);

CREATE TABLE secret_forums (
    id SERIAL PRIMARY KEY,
    users TEXT[]
);

CREATE TABLE secret_messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    username TEXT,
    sent_at TIMESTAMP,
    forum_id INT
);

CREATE TABLE secret_comments (
    id SERIAL PRIMARY KEY,
    content TEXT,
    message_id INT,
    forum_id INT,
    username TEXT,
    sent_at TIMESTAMP
);






