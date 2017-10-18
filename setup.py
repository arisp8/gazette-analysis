import sqlite3
import os, errno

db = sqlite3.connect('data/default')

# Takes care of setting up the local SQLite database
def setup_local_db():
    # Creates the data folder if not exists
    try:
        os.makedirs('data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    setup_ministries_table()
    setup_mps_table()
    setup_terms_table()
    setup_issues_table()
    setup_signatures_table()

# Sets up default table for ministries
def setup_ministries_table():
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ministries(
            id INTEGER PRIMARY KEY,
            name TEXT
        );
    ''')

# Sets up default table for MP's (Members of Parliament)
def setup_mps_table():
    cursor = db.cursor()

    # Important note: MPs on their own are not attached or affiliated with any ministries by default. This
    # relationship can only be found from the `terms` table which specifies the time periods where x MP was in
    # y ministry.

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mps(
            id INTEGER PRIMARY KEY,
            name TEXT,
            political_party TEXT,
            birthdate INTEGER
        );
    ''')
    db.commit()

# Sets up default table for minister's terms
def setup_terms_table():
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY,
            mp_id INTEGER,
            ministry_id INTEGER,
            date_from INTEGER,
            date_to INTEGER,
            FOREIGN KEY(mp_id) REFERENCES mps(id),
            FOREIGN KEY(ministry_id) REFERENCES ministries(id)
        );
    ''')

# Sets up default table for fek issues
def setup_issues_table():
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY,
            title TEXT,
            type TEXT,
            number INTEGER,
            file TEXT,
            date INTEGER
        );
            
    ''')

# Sets up default table for the signatures found in fek issues
def setup_signatures_table():
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signatures(
            id INTEGER PRIMARY KEY,
            mp_id INTEGER,
            fek_id INTEGER,
            data TEXT,
            FOREIGN KEY(mp_id) REFERENCES mps(id),
            FOREIGN KEY(fek_id) REFERENCES issues(id)
        );
    ''')


setup_local_db()