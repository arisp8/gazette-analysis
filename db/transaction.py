import sqlite3

# This class defines all required transactions for saving, adding and altering entities in an SQLite database
class Transaction:

    __db = None

    def __init__(self, db_name = 'default'):
        __db = sqlite3.connect('data/' + db_name)

