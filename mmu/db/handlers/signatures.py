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
        return TransactionHandler.select_all(self, table='signatures', conditions=conditions, joins=joins)

    # Selects (up to) one signature that matches the conditions given
    def load_one(self, conditions = None):
        return TransactionHandler.select_one(self, table='signatures', conditions=conditions)

    # Selects all signatures that match the conditions given
    def load_all(self, conditions = None):
        return TransactionHandler.select_all(self, table='signatures', conditions=conditions)

    # Saves a signature in the sqlite database
    def create(self, person_id, issue_id, data):
        params = {'person_id': person_id, 'issue_id': issue_id, 'data': data}
        TransactionHandler.insert(self, table='signatures', params=params)

# Handler class for saving raw signatures
class RawSignatureHandler(TransactionHandler):

    # Default constructor for the Raw Signature Handler
    def __init__(self, db_name='default'):
        TransactionHandler.__init__(self, db_name)

    # Loads a signature by id
    def load_by_id(self, id):
        conditions = {'id': [id]}
        return self.load_one(conditions)

    # Loads all signatures by person_name when given conditions are matched
    def load_all_by_person_name(self, person_name):
        conditions = {'person_name': [person_name]}
        return TransactionHandler.select_all(self, table='raw_signatures', conditions=conditions)

    # Selects (up to) one signature that matches the conditions given
    def load_one(self, conditions=None):
        return TransactionHandler.select_one(self, table='raw_signatures', conditions=conditions)

    # Selects all signatures that match the conditions given
    def load_all(self, conditions=None, group_by=None):
        return TransactionHandler.select_all(self, table='raw_signatures', conditions=conditions, group_by=group_by)

    # Saves a signature in the sqlite database
    def create(self, person_name, role, issue_title, issue_date):
        params = {'person_name': person_name, 'role': role, 'issue_title': issue_title, 'issue_date' : issue_date}
        TransactionHandler.insert(self, table='raw_signatures', params=params)

    # Saves multiple signatures contained in a list
    def create_multiple(self, inserts):
        TransactionHandler.insert_multiple(self, 'raw_signatures', inserts)

    # Updates database entries that match given conditions changing their values to given params
    def update(self, params, conditions=None):
        TransactionHandler.update(self, 'raw_signatures', params, conditions)

    # Finds the most common role given a person's name and some conditions
    def find_most_common_role(self, conditions, person_name):
        conditions['person_name'] = [person_name]
        formatted_conditions = TransactionHandler.format_conditions(self, 'raw_signatures', conditions)
        query = ''' 
                    SELECT role,
                    COUNT(role) AS role_occurence 
                    FROM   raw_signatures
                    {conditions}
                    GROUP BY `role`
                    ORDER BY `role_occurence` DESC
                    LIMIT    1;
                '''.format(conditions=formatted_conditions)

        return TransactionHandler.execute_select_all(self, query=query)