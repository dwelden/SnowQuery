from string import ascii_uppercase, digits

import prettytable as pt
from SnowflakeConnectionPK import get_connection_parameters
import snowflake.connector
from snowflake.connector import DictCursor

class Model:
    def __init__(self):
        ''' Establish connection to Snowflake '''

        # Load Snowflake connection parameters
        connection_parameters = get_connection_parameters()

        # Connect to Snowflake and create cursors
        self.cnxn = snowflake.connector.connect(**connection_parameters)
        self.cursor = self.cnxn.cursor()
        self.dcursor = self.cnxn.cursor(DictCursor)
        self.object_types = [
            'Tables',
            'Views',
            'Stages',
            'File Formats',
            'Functions',
            'Procedures',
            'Dynamic Tables',
            'Pipes',
            'Streams',
            'Tasks',
            'Sequences'
        ]

    def get_databases(self, tree_data, scope):
        ''' Get databases '''
        dbs = self.get_metadata('Databases', scope)

        # Add databases to tree
        for db in dbs:
            db_key = self.format_identifier(db)
            tree_data.Insert('',db_key,db,['Database',])

    def get_schemas(self, tree_data, scope):
        ''' Get database schemas '''
        schemas = self.get_metadata('Schemas', scope)

        # Add schemas to tree
        for db, schema in schemas:
            db_key = db
            formatted_db = f'{self.format_identifier(db)}'
            formatted_schema = f'{self.format_identifier(schema)}'
            schema_key = f'{formatted_db}.{formatted_schema}'
            tree_data.Insert(db_key,schema_key,schema,['Schema',])

    def get_schema_objects(self, tree_data, object_type, scope):
        ''' Get schema objects'''
        schema_objects = self.get_metadata(object_type, scope)

        # Add schema objects to tree
        for db, schema, name in schema_objects:
            formatted_db = f'{self.format_identifier(db)}'
            formatted_schema = f'{self.format_identifier(schema)}'
            formatted_name = f'{self.format_identifier(name)}'

            # Add schema object types to tree
            for obj_type in self.object_types:
                # INFORMATION_SCHEMA has only Views
                if schema == 'INFORMATION_SCHEMA' and obj_type != 'Views':
                    continue
                obj_type_key = f'{formatted_db}.{formatted_schema}-{obj_type}'
                if not tree_data.tree_dict.get(obj_type_key):
                    # Add schema object type to tree
                    schema_key = f'{formatted_db}.{formatted_schema}'
                    tree_data.Insert(schema_key,obj_type_key,obj_type,[obj_type,])

            object_type_key = f'{formatted_db}.{formatted_schema}-{object_type}'
            schema_object_key = f'{formatted_db}.{formatted_schema}.{formatted_name}'
            tree_data.Insert(object_type_key,schema_object_key,name,['leaf',])

    def format_identifier(self, id):
        ''' Quote format the identifier if needed.
            Unquoted identifiers:
                a. Start with letter A-Z or an underscore (_)
                b. Contain only letters A-Z, underscores, digits 0-9, and dollar signs ($)
                c. To use the double quote character (") inside a quoted identifier, use two quotes.
        '''
        unquoted_ok = True
        unquoted_intials = ascii_uppercase + '_'
        unquoted_characters = set(unquoted_intials + digits + '$')

        id_initial = id[0]
        id_characters = set(id)
        if id_initial not in unquoted_intials:
            unquoted_ok = False     # rule a.
        elif id_characters - unquoted_characters:
            unquoted_ok = False     # rule b.

        if unquoted_ok:
            return id
        else:
            return f'''"{id.replace('"','""')}"'''  # rule c.

    def get_metadata(self, object_type, scope):
        ''' Get requested database metadata from Snowflake '''
        sql = f'SHOW {object_type} IN {scope}'

        # Set database name column, and filter for functions and procedures
        if object_type in ('Functions', 'Procedures'):
            dbname = 'catalog_name'
            filter = """ WHERE "is_builtin" = 'N'"""
        else:
            dbname = 'database_name'
            filter = None

        # Build results SQL
        if object_type == 'Databases':
            results_sql = 'SELECT "name"'
        elif object_type == 'Schemas':
            results_sql = 'SELECT "database_name", "name"'
        elif object_type in ('Functions', 'Procedures'):
            results_sql = f'''SELECT "{dbname}", "schema_name", REGEXP_REPLACE("arguments", ' RETURN .*', '') as "name"'''
        else:
            results_sql = f'SELECT "{dbname}", "schema_name", "name"'
        results_sql += ' FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))'
        if filter:
            results_sql += filter
        results_sql += ' ORDER BY "name"'
        
        # Build and execute query
        query = f"""
        declare
            res resultset;
        begin
            {sql};
            res := ({results_sql});
            return table (res);
        end;
        """
        self.dcursor.execute(query)

        # Extract and return results
        if object_type == 'Databases':
            metadata = [row['name'] for row in self.dcursor]
        elif object_type == 'Schemas':
            metadata = [
                    [row[dbname],
                    row['name']]
                for row in self.dcursor]
        else:
            metadata = [
                    [row[dbname],
                    row['schema_name'],
                    row['name']]
                for row in self.dcursor]

        return metadata

    def run_query(self, query):
        ''' Submit query to Snowflake and return formatted output '''
        query_details = {
            "query_id"       : '',
            "query_duration" : '',
            "query_error"    : False
        }
        try:
            self.cursor.execute(query)
            output = pt.from_db_cursor(self.cursor)

            # Format output as Markdown table using pretty table
            output.set_style(pt.MARKDOWN)
            output.align = "l"
            for column in self.cursor.description:
                if column.precision:
                    output.align[column.name] = "r"

            query_details['query_id'] = self.cursor.sfqid
            query_details['query_duration'] = self.query_duration()
        except Exception as e:
            query_details['query_error'] = True
            output = e.__repr__()
        return((output, query_details))

    def query_duration(self):
        ''' Get duration of last execute query '''
        query_id = self.cursor.sfqid
        sql = f"""
            select
                to_varchar(
                    time_from_parts(0, 0, 0, total_elapsed_time * 1000000)
                ) as elapsed
            from table(information_schema.query_history_by_session())
            where query_id = '{query_id}'"""
        try:
            query_duration = self.cursor.execute(sql).fetchone()[0]
        except:
            query_duration = ''
        return query_duration
