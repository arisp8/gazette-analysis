from mmu.db.transaction import TransactionHandler
class MinisterHandler(TransactionHandler):

    # Default constructor for Ministers
    def __init__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Loads a minister from the database using his id
    def load_by_id(self, id):
        conditions = {'id' : [id]}
        return self.load(conditions)

    # Loads a minister from the database by matching his name
    def load_by_name(self, name):
        conditions = {'name' : ['%name%', 'LIKE']}
        return self.load(conditions)

    # Selects (up to) one minister who matches the conditions given
    def load_one(self, conditions = None):
        return TransactionHandler.select_one(self, table='ministers', conditions=conditions,
                                         joins={'terms' : ['INNER', 'ministers.id = terms.minister_id'],
                                                'ministries' : ['INNER', 'ministries.id = terms.ministry_id']})

    # Selects all ministers who match the conditions given
    def load_all(self, conditions = None):
        return TransactionHandler.select_all(self, table='ministers', conditions=conditions,
                                         joins={'terms' : ['INNER', 'ministers.id = terms.minister_id'],
                                                'ministries' : ['INNER', 'ministries.id = terms.ministry_id']})

    # Creates a new minister
    def create(self, name, political_party, birthdate):
        TransactionHandler.insert(self, 'ministers', {'name' : name, 'political_party' : political_party,
                                                      'birthdate' : birthdate})

    # Updates a minister's information
    def update(self, id, params):
        conditions = {'id' : [id]}
        TransactionHandler.update(self, table='ministers', params=params, conditions=conditions)
    