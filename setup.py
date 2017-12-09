import sqlite3
import os, errno
import sys


# Sets up required elements for the application
# @todo: Install required libraries
def setup():
    if len(sys.argv) > 1:

        arg1 = sys.argv[1]

        # if --clean_install is specified then the previous sqlite database is deleted.
        if arg1 == '--clean_install':
            print("Deleting SQLite Database")
            delete_sqlite_database()

        print("Setting up local database from scratch")
        setup_local_db()


def delete_sqlite_database():
    try:
        os.remove('data/default')
        print("SQLite database has been deleted")
    except FileNotFoundError as e:
        print("File has not been found")
    except PermissionError as e:
        print("File could not be deleted")


# Takes care of setting up the local SQLite database
def setup_local_db():

    # Creates the data folder if not exists
    try:
        os.makedirs('mmu/data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    db = sqlite3.connect('mmu/data/default')
    cursor = db.cursor()

    # Executes the default.sql to create default database schema
    install_sql = open('install/default.sql', 'r', encoding='utf8').read()
    cursor.executescript(install_sql)

    db.commit()
    cursor.close()
    db.close()


setup()
