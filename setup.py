import sqlite3
import os, errno
import sys

# Sets up required elements for the application
# @todo: Install required libraries
def setup():
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
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
        pass



# Takes care of setting up the local SQLite database
def setup_local_db():
    db = sqlite3.connect('data/default')
    cursor = db.cursor()
    # Creates the data folder if not exists
    try:
        os.makedirs('data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    setup_ministries_table(cursor)
    setup_persons_table(cursor)
    setup_cabinets_table(cursor)
    setup_issues_table(cursor)
    setup_signatures_table(cursor)
    setup_positions_table(cursor)

# Sets up default table for ministries
def setup_ministries_table(cursor):

    # This table contains all greek ministries. Name changes and restructuring count as different ministries.

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ministries(
            id INTEGER PRIMARY KEY, 
            name TEXT -- The Ministry's name, e.g. "Υπουργείο Οικονομικών" (Ministry of Finance)
        );
    ''')

# Sets up default table for persons (Most of them Members of Parliament, but not all)
def setup_persons_table(cursor):

    # Important note: Persons on their own are not attached or affiliated with any ministries by default. This
    # relationship can only be found from the `positions` table which specifies the time periods where x person was in
    # y ministry.

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL, -- A person's full name
            political_party TEXT, -- The political party of someone, or Independent if there's no affiliation
            birthdate INTEGER -- UNIX timestamp of a person's date of birth
        );
    ''')

# Sets up default table for cabinets
def setup_cabinets_table(cursor):

    # This table contains the cabinets of greece. An example cabinet is the active one at the time of writing:
    # Link: https://en.wikipedia.org/wiki/Second_Cabinet_of_Alexis_Tsipras

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cabinets (
            id INTEGER PRIMARY KEY, 
            title TEXT NOT NULL, -- The cabinet's title, e.g. "Κυβέρνηση Αλέξη Τσίπρα Σεπτεμβρίου 2015"
            description TEXT, -- A general description for the cabinet
            date_from INTEGER NOT NULL, -- UNIX timestamp containing the day the cabinet was formed
            date_to INTEGER NOT NULL -- UNIX timestamp containing the day the cabinet disbanded, 0 if still active
        );
    ''')

# Sets up default positions table for persons
def setup_positions_table(cursor):

    # This table specifies in which ministry a person is and during which time

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY,
            role TEXT, -- The person's role, e.g. Minister, Deputy etc.
            date_from INTEGER NOT NULL, -- UNIX timestamp when the person got this position
            date_to INTEGER NOT NULL, -- UNIX timestamp when the person stopped being in this position
            person_id INTEGER, -- Shows which person's position we're referencing
            ministry_id INTEGER, -- Shows in which ministry this person is
            FOREIGN KEY(person_id) REFERENCES persons(id),
            FOREIGN KEY(ministry_id) REFERENCES ministries(id)
        );
    ''')

# Sets up default table for fek issues
def setup_issues_table(cursor):

    # Helper table storing information about the fek issues we have saved

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY,
            title TEXT, -- The title of the fek issue
            type TEXT, -- The type of the fek issue, e.g A, B, 	Α.Σ.Ε.Π. etc.
            number INTEGER, -- The number of the issue
            file TEXT, -- The issues pdf file location
            date INTEGER -- UNIX timestamp when this fek issue was published
        );  
    ''')

# Sets up default table for the signatures found in fek issues
def setup_signatures_table(cursor):

    # Holds information about the signatures scraped from the fek issues
    # Will be useful in the final statistical analysis

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signatures(
            id INTEGER PRIMARY KEY,
            person_id INTEGER, -- The person this signature belongs to
            fek_id INTEGER, -- The fek issue this signature was scraped from
            data TEXT, -- Additional data for the signature, possibly extracted from the pdf
            FOREIGN KEY(person_id) REFERENCES persons(id),
            FOREIGN KEY(fek_id) REFERENCES issues(id)
        );
    ''')

setup()