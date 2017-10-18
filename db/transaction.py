import sqlite3
import os

# This class defines all required transactions for saving, adding and altering entities in an SQLite database
class TransactionHandler:

    def __init__(self, db_name = 'default'):
        self.__db = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '/../data/' + db_name)
        # Sets the function that turns tuples into key-value dictionaries
        self.__db.row_factory = self.dict_factory


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

        query = '''
            INSERT INTO {t} ({c}) 
            VALUES({v})
        '''.format(t=table, c=columns, v=values)

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

    def format_conditions(self, table, conditions = None):
        formatted_conditions = ""

        # The default case with no conditions specified will match everything
        # @TODO: Benchmark and see if WHERE 1 = 1 costs time, if yes remove the WHERE clause when 0 conditions are given
        if not conditions:
            formatted_conditions = "1 = 1"
        else:
            count = 0
            num_conditions = len(conditions)

            for condition_name in conditions:

                condition_value = self.format_value(conditions[condition_name][0])

                # Default separator of none given is AND
                if len(conditions[condition_name]) == 3:
                    separator = " {} ".format(conditions[condition_name][2])
                else:
                    separator = " AND "

                # Default operator if none given is =
                operator = "="
                if len(conditions[condition_name]) > 1:
                    operator = conditions[condition_name][1]

                # No separator needed if this is the last condition
                if count == num_conditions - 1:
                    separator = ""

                formatted_conditions += "{table}.{name} {operator} {value} {separator}".format(table= table,
                    name=condition_name, operator=operator, value=condition_value, separator=separator)
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
        formatted_conditions = self.format_conditions(table, conditions)

        query = '''
            UPDATE {t}
            SET {v} 
            WHERE {c}
        '''.format(t=table, v=values, c=formatted_conditions)
        cursor.execute(query)

        self.__db.commit()

    # Formats joins to be used in a SELECT query
    # @param joins A dictionary in the format table_name : [INNER/LEFT,ON]
    def format_joins(self, joins = None):
        formatted_joins = ""

        if joins:
            for join_table in joins:
                type = joins[join_table][0].upper()
                on = joins[join_table][1]
                formatted_joins += "{type} JOIN {table} ON {on} ".format(type=type, table = join_table, on=on)

        return formatted_joins


    # Builds a SELECT statement for the SQLite database using the parameters given
    # @param table The table to select FROM
    # @param params A list of column names
    # @param condtions A dictionary containing conditions in the format:
    #   condition_name : [condition_value, operator, separator]. If separator is not given AND will be used
    # @param joins A dictionary in the format table_name : [INNER/LEFT,ON]
    # @TODO: Possibly allow adding LIMIT start, offset
    def select_query(self, table, columns = None, conditions = None, joins = None):

        # If no columns are given we'll select all columns
        formatted_columns = "*"

        if columns:
            formatted_columns = ""
            separator = ","

            for column_name in columns[:-1]:
                formatted_columns += column_name + separator
            else:
                separator = ""
                formatted_columns += columns[-1] + separator

        # If no condition is given, we will match everything
        formatted_conditions = self.format_conditions(table, conditions)
        formatted_joins = self.format_joins(joins)


        query = '''
            SELECT {cols} 
            FROM {t} 
            {j} 
            WHERE {cond}
        '''.format(cols=formatted_columns, t=table,j=formatted_joins,cond=formatted_conditions)
        return query

    # Turns a row into a key : value dictionary from a tuple
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    # Selects one element that matches given conditions
    def select_one(self, table, columns=None, conditions=None, joins=None):
        cursor = self.__db.cursor()
        query = self.select_query(table, columns, conditions, joins)
        cursor.execute(query)
        return cursor.fetchone()

    # Selects many elements that match given conditions
    # @param amount The amount of elements to return
    def select_many(self, table, columns=None, conditions=None, joins=None, limit = 1):
        cursor = self.__db.cursor()
        query = self.select_query(table, columns, conditions, joins)
        print(query)
        cursor.execute(query)
        return cursor.fetchmany(limit)

    # Selects all elements that match a query
    def select_all(self, table, columns=None, conditions=None, joins=None):
        cursor = self.__db.cursor()
        query = self.select_query(table, columns, conditions, joins)
        cursor.execute(query)
        return cursor.fetchall()