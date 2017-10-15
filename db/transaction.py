import sqlite3

# This class defines all required transactions for saving, adding and altering entities in an SQLite database
class TransactionHandler:

    def __init__(self, db_name = 'default'):
        self.__db = sqlite3.connect('../data/' + db_name)

    # Builds an INSERT statement for the SQLite database using the parameters specified in params
    # @param table The table
    # @param params A dictionary of all columns and their values accordingly
    def insert(self, table, params):
        cursor = self.__db.cursor()
        columns = ""
        values = ""
        separator = ","
        count = 0

        for column_name in params:

            # Doesn't use a comma after the last element
            if count == len(params) - 1:
                separator = ""

            columns += column_name + separator
            values += ":" + column_name + separator

            count += 1

        query = "INSERT INTO {} ({}) VALUES({})".format(table, columns, values)
        cursor.execute(query, params)
        self.__db.commit()

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def format_value(self, value):
        if self.is_number(value):
            return value
        else:
            return "'" + value + "'"

    def format_conditions(self, conditions = None):
        formatted_conditions = ""

        # The default case with no conditions specified will match everything
        if not conditions:
            formatted_conditions = "1 = 1"
        else:
            count = 0
            num_conditions = len(conditions)

            for condition_name in conditions:

                condition_value = self.format_value(conditions[condition_name][0])

                # Default separator of none given is AND
                if len(conditions[condition_name]) == 3:
                    separator = conditions[condition_name][2]
                else:
                    separator = "AND"

                # Default operator if none given is =
                operator = "="
                if len(conditions[condition_name]) > 1:
                    operator = conditions[condition_name][1]

                # No separator needed if this is the last condition
                if count == num_conditions - 1:
                    separator = ""

                formatted_conditions += "{} {} {} {}".format(condition_name, operator, condition_value, separator)
                count += 1

        return formatted_conditions

    # Builds an UPDATE statement for the SQLite database using the parameters given
    # @param table The table to update
    # @param params A dictionary containing column names and values to change for this table
    # @param condtions A dictionary containing conditions in the format:
    #   condition_name : [condition_value, operator, separator]. If separator is not given AND will be used
    def update(self, table, params, conditions = None):
        cursor = self.__db

        # Formatting the value changes for the UPDATE statement
        values = ""
        separator = ","
        count = 0
        num_params = len(params)

        for column_name in params:
            value = self.format_value(params[column_name])
            if count ==  num_params - 1:
                separator = ""
            values += "{} = {}{}".format(column_name, value, separator)
            count += 1

        # Formatting the conditions for the UPDATE statement
        formatted_conditions = self.format_conditions(conditions)



        query = "UPDATE {} SET {} WHERE {}".format(table, values, formatted_conditions)
        cursor.execute(query)

        self.__db.commit()