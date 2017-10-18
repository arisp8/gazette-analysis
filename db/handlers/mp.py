from mmu.db.transaction import TransactionHandler

# Handler class for creating, searching and editing ministers data
class MpHandler(TransactionHandler):

    # Default constructor for Ministers
    def __init__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Loads a mp from the database using his id
    def load_by_id(self, id):
        conditions = {'id' : [id]}
        return self.load(conditions)

    # Loads a mp from the database by matching his name
    def load_by_name(self, name):
        conditions = {'name' : ['%name%', 'LIKE']}
        return self.load(conditions)

    # Selects (up to) one mp who matches the conditions given
    def load_one(self, conditions = None):
        return TransactionHandler.select_one(self, table='mps', conditions=conditions,
                                         joins={'terms' : ['INNER', 'mps.id = terms.mp_id'],
                                                'ministries' : ['INNER', 'ministries.id = terms.ministry_id']})

    # Selects all mps who match the conditions given
    def load_all(self, conditions = None):
        return TransactionHandler.select_all(self, table='mps', conditions=conditions,
                                         joins={'terms' : ['INNER', 'mps.id = terms.mp_id'],
                                                'ministries' : ['INNER', 'ministries.id = terms.ministry_id']})

    # Creates a new mp
    def create(self, name, political_party, birthdate):
        TransactionHandler.insert(self, 'mps', {'name' : name, 'political_party' : political_party,
                                                      'birthdate' : birthdate})

    # Updates a mp's information
    def update(self, id, params):
        conditions = {'id' : [id]}
        TransactionHandler.update(self, table='mps', params=params, conditions=conditions)
