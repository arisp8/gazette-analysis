from mmu.db.transaction import TransactionHandler

class IssueHandler(TransactionHandler):

    # Default constructor for the Issue handler
    def __init__(self, db_name='default'):
        TransactionHandler.__init__(self, db_name)

    # Creates new record in the database for the issue
    def create(self, title, type, number, file, date):
        values = {'title' : title, 'type' : type, 'number' : number, 'file' : file, 'date' : date}
        TransactionHandler.insert(self, 'issues', values)

    # Loads information about an issue by its title
    def load_by_title(self, title):
        conditions = {'title' : [title]}
        return TransactionHandler.select_one(self, table='issues', conditions=conditions)

    # Loads all issues
    def load_all(self):
        return TransactionHandler.select_all(self, table='issues')