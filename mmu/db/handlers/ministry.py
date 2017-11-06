from mmu.db.transaction import TransactionHandler

# Handler class for altering and creating ministry records
class MinistryHandler(TransactionHandler):

    def __int__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Creates a new ministry
    def create(self, name, description, established = 0, disbanded = 0):
        params = {'name' : name, 'description' : description, 'established' : established, 'disbanded' : disbanded}
        print(params)
        TransactionHandler.insert(self,table='ministries',params=params)

    # Updates a ministry based on the id given
    def update(self, id, params):
        conditions = {'id' : [id]}
        TransactionHandler.update(self, table='ministries', params=params, conditions=conditions)

    # Loads a ministry by name
    def load_by_name(self, name):
        conditions = {'name' : [name]}
        return TransactionHandler.select_one(self, 'ministries', conditions=conditions)

    # Loads all ministries
    def load_all(self):
        return TransactionHandler.select_all(self, 'ministries')
