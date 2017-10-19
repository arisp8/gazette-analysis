from mmu.db.transaction import TransactionHandler

# Handler class for altering and creating cabinets data
class CabinetHandler(TransactionHandler):

    def __int__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Creates a new cabinet
    def create(self, title, description, date_from, date_to):
        params = {'title' : title, 'description' : description, 'date_from' : date_from,
                  'date_to' : date_to}
        TransactionHandler.insert(self,table='cabinets',params=params)

    # Updates a cabinet given its id
    def update(self, id, params):
        conditions = {'id' : [id]}
        TransactionHandler.update(self, table='cabinets', params=params, conditions=conditions)