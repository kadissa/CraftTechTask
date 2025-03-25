import sqlite3

DEBUG = True
DB_PATH = "database.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Files (
            id INTEGER PRIMARY KEY, 
            name TEXT UNIQUE
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tags (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            file_id INTEGER, 
            FOREIGN KEY (file_id) REFERENCES Files(id)
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attributes (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            value TEXT, 
            tag_id INTEGER, 
            FOREIGN KEY (tag_id) REFERENCES Tags(id)
        )""")
        conn.commit()


if __name__ == '__main__':
    init_db()
