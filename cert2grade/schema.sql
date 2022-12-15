DROP TABLE IF EXISTS user;

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    settings TEXT NOT NULL
);

CREATE TABLE requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    tstamp INTEGER NOT NULL,
    files INTEGER NOT NULL,
    size REAL NOT NULL, 
    duration REAL NOT NULL
);

CREATE TABLE files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    request_id INTEGER NOT NULL,
      
    FOREIGN KEY(request_id) REFERENCES requests(request_id)
)