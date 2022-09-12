import snowflake.connector
from snowflake.connector import DictCursor
import prettytable as pt
import json
import PySimpleGUI as sg
from sys import argv
import os.path

def show_window(cursor, dcursor):
    # Window theme settings
    sg.theme('DarkGray15')
    UI_font = ("Segoe UI", 12)
    fixed_font = ('Consolas', 12)
    run = '▶'

    tree_data = build_database_tree(dcursor)

    # Create the Window layout
    left_column = sg.Frame('Databases',
        [   [sg.Tree(data=tree_data,
                    headings=[],
                    auto_size_columns=True,
                    select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                    col0_width=30,
                    key='-TREE-',
                    show_expanded=False,
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    )]],
        expand_x=True,
        expand_y=True)
    right_column = sg.Column(
        [  [sg.Text('Enter SQL command'),
            sg.Push(),
            sg.Button(run,tooltip='Run (F5)')],
           [sg.Multiline(
                size=(80,15),
                key='-query-',
                font=fixed_font,
                expand_x=True,
                expand_y=True)],
           [sg.Text('Output')],
           [sg.Multiline(
                size=(80,15),
                key='-output-',
                font=fixed_font,
                expand_x=True,
                expand_y=True,
                do_not_clear=False)]],
        expand_x=True,
        expand_y=True)
    layout = [[left_column, right_column]]

    # Create the Window
    icon = get_icon()
    window = sg.Window(
        title='Snow Query',
        icon=icon,
        layout=layout,
        font=UI_font,
        resizable=True,
        finalize=True)
    window.bind('<F5>', run)
    window.bind('<Control-q>', 'Quit')

    # Event Loop to process "events"
    while True:             
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Quit'):
            break
        elif event == '-TREE-':
            continue
        elif event == run:
            query = values["-query-"]
            if query:
                # Execute query and return output
                query_error, output = run_query(cursor, query)
                if query_error:
                    # Display error output
                    window['-output-'].print(
                        output,
                        colors=('red'))
                else:
                    # Display query output
                    window['-output-'].print(output)
            else:
                # Display help popup in approximate center of window
                window_location = window.current_location()
                window_size = window.size
                popup_location = (
                    window_location[0] + int(window_size[0]/2),
                    window_location[1] + int(window_size[1]/2))
                sg.popup(
                    'Enter a SQL command',
                    f'Press {run} or F5 to submit',
                    'Press Control-Q to quit',
                    font=UI_font,
                    title='',
                    location=popup_location)

    window.close()

    return

def build_database_tree(dcursor):
    tree_data = sg.TreeData()
    object_types = [
        'Tables',
        'Views',
        'Stages',
        'File Formats',
        'Sequences',
        'Pipes',
        'Streams',
        'Tasks',
        'Functions',
        'Procedures']

    # Get databases
    sql = 'SHOW DATABASES;'
    dbs = get_metadata(dcursor, sql)
    for db in dbs:
        # Add database to tree
        db_key = f'-{db}-'
        tree_data.Insert('',db_key,db,[])

        # Get database schemas
        sql = f'SHOW SCHEMAS IN DATABASE {db};'
        schemas = get_metadata(dcursor, sql)
        for schema in schemas:
            # Add schema to tree
            schema_key = f'-{db}.{schema}-'
            tree_data.Insert(db_key,schema_key,schema,[])

            # Get schema object types
            for object_type in object_types:
                # Add schema object type to tree
                object_type_key = f'-{db}.{schema}-{object_type}-'
                tree_data.Insert(schema_key,object_type_key,object_type,[])

                # Get schema objects
                sql = f'SHOW {object_type} IN SCHEMA {db}.{schema};'
                schema_objects = get_metadata(dcursor, sql)
                for schema_object in schema_objects:
                    # Add schema object to tree
                    schema_object_key = f'-{db}.{schema}.{schema_object}-'
                    tree_data.Insert(object_type_key,schema_object_key,schema_object,[])
                    
    return(tree_data)

def get_metadata(dcursor, sql):
    dcursor.execute(sql)
    sql2 = 'SELECT "name" FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))'
    if 'FUNCTIONS' in sql.upper() or 'PROCEDURES' in sql.upper():
        sql2 += """ WHERE "is_builtin" = 'N'"""
    dcursor.execute(sql2)
    metadata = [row['name'] for row in dcursor]
    return metadata

def run_query(cursor, query):
    query_error = False
    try:
        cursor.execute(query)
        output = pt.from_db_cursor(cursor)

        # Format output as Markdown table using pretty table
        output.set_style(pt.MARKDOWN)
        output.align = "l"
        for column in cursor.description:
            if column.precision:
                output.align[column.name] = "r"
    except Exception as e:
        query_error = True
        output = e.msg
    return((query_error,output))

def get_icon():
    icon = b'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'
    return icon

def main():

    # Load Snowflake connection parameters
    scp_pathname = os.path.dirname(argv[0])     # same path as this script
    scp_filename = 'SnowflakeConnectionParameters.json'
    scp_file = os.path.join(scp_pathname, scp_filename)
    with open(scp_file, 'r') as scp:
        connection_parameters = json.load(scp)

    # Connect to Snowflake and create cursors
    with snowflake.connector.connect(**connection_parameters) as cnxn:
        with cnxn.cursor() as cursor:
            with cnxn.cursor(DictCursor) as dcursor:

                # Show window and begin event loop
                show_window(cursor, dcursor)

if __name__ == '__main__':
    main()
