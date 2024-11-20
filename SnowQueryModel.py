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

    def __del__(self):
        ''' Cleanup connection to Snowflake '''

        # Connect to Snowflake and create cursors
        self.cursor.close()
        self.dcursor.close()
        self.cnxn.close()

    def get_schema_object_list(self, node_level, scope):
        ''' Get list of objects under the specified node '''
        schema_object_list = []
        add_object_header = True
        if node_level == 'Root':
            schema_object_list += self.get_databases(scope)
            schema_object_list += self.get_schemas(scope)
            for object_type in self.object_types:
                schema_object_list += self.get_schema_objects(object_type, scope, add_object_header)
        elif node_level == 'Database':
            schema_object_list += self.get_schemas(scope)
            for object_type in self.object_types:
                schema_object_list += self.get_schema_objects(object_type, scope, add_object_header)
        elif node_level == 'Schema':
            for object_type in self.object_types:
                schema_object_list += self.get_schema_objects(object_type, scope, add_object_header)
        elif node_level in self.object_types:
            add_object_header = False
            schema_object_list += self.get_schema_objects(node_level, scope, add_object_header)
        return schema_object_list

    def get_databases(self, scope):
        ''' Get databases '''
        dbs = self.get_metadata('Databases', scope)

        db_list = []
        for db in dbs:
            db_list.append(
                {
                    "parent": "",
                    "name": db,
                    "formatted_name": self.format_identifier(db),
                    "object_type": "Database"
                }
            )
        return db_list

    def get_schemas(self, scope):
        ''' Get database schemas '''
        schemas = self.get_metadata('Schemas', scope)

        schema_list = []
        for db, schema in schemas:
            formatted_db = f'{self.format_identifier(db)}'
            formatted_schema = f'{self.format_identifier(schema)}'
            schema_list.append(
                {
                    "parent": db,
                    "name": schema,
                    "formatted_name": f"{formatted_db}.{formatted_schema}",
                    "object_type": "Schema"
                }
            )
        return schema_list

    def get_schema_objects(self, object_type, scope, add_object_header):
        ''' Get schema objects'''
        schema_objects = self.get_metadata(object_type, scope)

        schema_object_list = []
        object_headers = []
        for db, schema, name in schema_objects:
            formatted_db = f'{self.format_identifier(db)}'
            formatted_schema = f'{self.format_identifier(schema)}'
            formatted_name = f'{self.format_identifier(name)}'
            object_header = {
                "parent": f"{formatted_db}.{formatted_schema}",
                "name": object_type,
                "formatted_name": f'{formatted_db}.{formatted_schema}.{object_type}',
                "object_type": "object_header"
            }
            if add_object_header and object_header not in object_headers:
                schema_object_list.append(object_header)
                object_headers.append(object_header)

            schema_object_list.append(
                {
                    "parent": f"{formatted_db}.{formatted_schema}.{object_type}",
                    "name": name,
                    "formatted_name": f'{formatted_db}.{formatted_schema}.{formatted_name}',
                    "object_type": object_type
                }
            )
        return schema_object_list

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
        
        # Set database name column, and filter for functions and procedures
        if object_type in ('Functions', 'Procedures'):
            dbname = 'catalog_name'
            filter = """ WHERE "is_builtin" = 'N'"""
        else:
            dbname = 'database_name'
            filter = ''

        # Build parameters for results SQL
        if object_type == 'Databases':
            column_list = '"name"'
        elif object_type == 'Schemas':
            column_list = '"database_name", "name"'
        elif object_type in ('Functions', 'Procedures'):
            column_list = f'''"{dbname}", "schema_name", REGEXP_REPLACE("arguments", ' RETURN .*', '') as "name"'''
        else:
            column_list = f'"{dbname}", "schema_name", "name"'
        
        # Build and execute query
        query = f"""
        declare
            res resultset;
        begin
            SHOW TERSE {object_type} IN {scope};
            res := (SELECT {column_list} FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())) {filter} ORDER BY "name");
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
