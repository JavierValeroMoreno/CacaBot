CREATE TABLE Logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level     TEXT    NOT NULL,
    class_name    TEXT    NOT NULL,
    method_name   TEXT    NOT NULL,
    error_message TEXT    NOT NULL,
    created_at    TEXT    NOT NULL
);
