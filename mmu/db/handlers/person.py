from mmu.db.transaction import TransactionHandler

# Handler class for creating, searching and editing persons data
class PersonHandler(TransactionHandler):

    # Default constructor for Persons
    def __init__(self, db_name = 'default'):
        TransactionHandler.__init__(self, db_name)

    # Loads a person from the database using his id
    def load_by_id(self, id):
        conditions = {'id' : [id]}
        return self.load_one(conditions)

    # Loads a person from the database by matching his name
    def load_by_name(self, name):
        conditions = {'name' : ['%' + name + '%', 'LIKE']}
        return self.load_one(conditions)

    # Selects (up to) one person who matches the conditions given
    def load_one(self, conditions = None):
        return TransactionHandler.select_one(self, table='persons', conditions=conditions)

    # Selects all persons who match the conditions given
    def load_all(self, conditions = None):
        return TransactionHandler.select_all(self, table='persons', conditions=conditions)

    # Creates a new person
    def create(self, name, political_party, birthdate):
        values = {'name' : name, 'political_party' : political_party, 'birthdate' : birthdate}
        TransactionHandler.insert(self, table='persons', params=values)

    # Updates a person's information
    def update(self, id, params):
        conditions = {'id' : [id]}
        TransactionHandler.update(self, table='persons', params=params, conditions=conditions)

    # Create a new position
    def save_position(self, role, date_from, date_to, person_id, ministry_id, cabinet_id):
        values = {'role' : role, 'date_from' : date_from, 'date_to' : date_to, 'person_id' : person_id,
                  'ministry_id' : ministry_id, 'cabinet_id' : cabinet_id}
        TransactionHandler.insert(self, table='positions', params=values)

    # Loads a position given some conditions
    def load_position(self, conditions):
        return TransactionHandler.select_one(self, 'positions', conditions=conditions)
