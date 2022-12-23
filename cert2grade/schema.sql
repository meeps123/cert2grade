DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS files;

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    verified INTEGER DEFAULT 0 NOT NULL, 
    password TEXT NOT NULL,
    settings TEXT NOT NULL
);

CREATE TABLE requests ( 
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    code TEXT UNIQUE NOT NULL,
    start_timestamp INTEGER NOT NULL,
    files INTEGER NOT NULL,
    size REAL NOT NULL, 
    end_timestamp INTEGER NOT NULL,
    CONSTRAINT user_id_fk
        FOREIGN KEY (user_id) 
        REFERENCES user(user_id) ON DELETE CASCADE
);

CREATE TABLE files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    request_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    size REAL NOT NULL,
    has_thumbnail INTEGER NOT NULL,
    hsp TEXT,
    status TEXT ,
    score REAL,
    type TEXT,
    remarks TEXT,
    CONSTRAINT request_id_fk
        FOREIGN KEY (request_id)
        REFERENCES requests(request_id) ON DELETE CASCADE
);