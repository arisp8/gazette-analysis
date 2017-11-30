from mmu.db.transaction import TransactionHandler

# Handler class for saving end accessing signatures
class SignatureHandler(TransactionHandler):

    # Default constructor for the Signature Handler
    def __init__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Loads a signature by id
    def load_by_id(self, id):
        conditions = {'id' : [id]}
        return self.load_one(conditions)

    # Loads all signatures by person_name when given conditions are matched
    def load_all_by_person_name(self, person_name, conditions = None):
        joins = {'persons' : ['INNER', 'signatures.person_id = persons.id']}

        if not conditions:
            conditions = {}

        conditions['persons.name'] = [person_name]
        print(conditions)
        return TransactionHandler.select_all(self, table='signatures', conditions=conditions, joins=joins)

    # Selects (up to) one signature that matches the conditions given
    def load_one(self, conditions = None):
        return TransactionHandler.select_one(self, table='signatures', conditions=conditions)

    # Selects all signatures that match the conditions given
    def load_all(self, conditions = None):
        return TransactionHandler.select_all(self, table='signatures', conditions=conditions)