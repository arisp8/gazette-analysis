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

    # Selects (up to) one signature that matches the conditions given
    def load_one(self, conditions = None, table = 'signatures'):
        return TransactionHandler.select_one(self, table=table, conditions=conditions)

    # Selects all signatures that match the conditions given
    def load_all(self, conditions = None, table = 'signatures'):
        return TransactionHandler.select_all(self, table=table, conditions=conditions)