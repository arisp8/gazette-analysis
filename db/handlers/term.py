from mmu.db.transaction import TransactionHandler

# Handler class for altering and creating terms data
class TermHandler(TransactionHandler):

    def __int__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Creates a new term
    def create(self, minister_id, ministry_id, date_from, date_to):
        params = {'minister_id' : minister_id, 'ministry_id' : ministry_id, 'date_from' : date_from,
                  'date_to' : date_to}
        TransactionHandler.insert(self,table='terms',params=params)

    # Updates a term given its id
    def update(self, id, params):
        conditions = {'id' : [id]}
        TransactionHandler.update(self, table='terms', params=params, conditions=conditions)