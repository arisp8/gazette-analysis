from mmu.db.transaction import TransactionHandler

# Handler class for altering and creating ministry records
class MinistryHandler(TransactionHandler):

    def __int__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Creates a new ministry
    def create(self, name):
        params = {'name:' : name}
        TransactionHandler.insert(self,table='ministries',params=params)

    # Updates a ministry based on the id given
    def update(self, id, params):
        conditions = {'id' : [id]}
        TransactionHandler.update(self, table='ministries', params=params, conditions=conditions)