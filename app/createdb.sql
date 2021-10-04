create table users(
    id integer primary key,
    mail VARCHAR(255),
    password VARCHAR(255),
    use BOOLEAN NOT NULL CHECK (use IN (0, 1))
);