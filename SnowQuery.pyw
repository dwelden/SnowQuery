import json
import os.path
import threading
from sys import argv

import prettytable as pt
import PySimpleGUI as sg
import snowflake.connector
from snowflake.connector import DictCursor

def show_window(cursor, dcursor):
    # Window theme settings
    sg.theme('DarkGray15')
    UI_font = ("Segoe UI", 11)
    fixed_font = ('Consolas', 11)

    # Event labels
    run_event     = '▶'      #F5
    new_event     = 'New      Ctrl+N'
    open_event    = 'Open     Ctrl+O'
    save_event    = 'Save     Ctrl+S'
    save_as_event = 'Save As...'
    quit_event    = 'Quit     Ctrl+Q'
    help_event    = 'Help     F1'
    about_event   = 'About'

    # Query file name and label
    query_file = None
    new_query = 'New Query'
    
    # Create the Window layout
    menu_def = [
        ['&File',
            ['&' + new_event,
             '&' + open_event,
             '&' + save_event,
             save_as_event,
             '---',
             '&' + quit_event]],
        ['&Help',
            ['&' + help_event,
             '&' + about_event]]]
    tree_data = sg.TreeData()
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
        [  [sg.Text(new_query,key='-QUERYNAME-'),
            sg.Push(),
            sg.Button(run_event,tooltip='Run (F5)')],
           [sg.Multiline(
                size=(80,15),
                key='-QUERY-',
                font=fixed_font,
                expand_x=True,
                expand_y=True)],
           [sg.Text('Output')],
           [sg.Multiline(
                disabled=True,
                size=(80,15),
                key='-OUTPUT-',
                font=fixed_font,
                expand_x=True,
                expand_y=True)]],
        expand_x=True,
        expand_y=True)
    layout = [
        [sg.Menu(menu_def)],
        [left_column, right_column],
        [sg.StatusBar('Loading databases...',key='-STATUSBAR-')]]

    # Create the Window
    icon = get_icon()
    window = sg.Window(
        title='Snow Query',
        icon=icon,
        layout=layout,
        font=UI_font,
        resizable=True,
        finalize=True)
    window.bind('<F5>', run_event)
    window.bind('<Control-n>', new_event)
    window.bind('<Control-o>', open_event)
    window.bind('<Control-s>', save_event)
    window.bind('<Control-q>', quit_event)
    window.bind('<F1>', help_event)

    # Start thread to build database tree
    threading.Thread(
        target=build_database_tree,
        args=(window,dcursor,),
        daemon=True
    ).start()

    # Event Loop to process "events"
    while True:             
        event, values = window.read()
        if event in (sg.WIN_CLOSED, quit_event):
            break
        elif event == '-TREE-':
            continue
        elif event == new_event:
            query_file = new_file(window, new_query)
        elif event == open_event:
            query_file = open_file(window)
        elif event == save_event:
            save_file(window, query_file)
        elif event == save_as_event:
            query_file = save_file_as(window)
        elif event == help_event:
            show_help(window, run_event)
        elif event == about_event:
            show_about(window)
        elif event == run_event:
            query = values["-QUERY-"]
            run(window, query, cursor, run_event)

    window.close()
    del window

    return

def new_file(window, new_query):
    query_file = None
    window['-QUERYNAME-'].update(new_query)
    window['-QUERYNAME-'].set_tooltip(new_query)
    window['-QUERY-'].update('')
    window['-OUTPUT-'].update('')
    return query_file

def open_file(window):
    query_file = sg.popup_get_file(
        'Open',
        no_window=True,
        file_types=(('.SQL files','*.sql'),('All files','*.*')))
    if query_file:
        with open(query_file,'r') as f:
            text = f.read()
            window['-QUERYNAME-'].update(os.path.basename(query_file))
            window['-QUERYNAME-'].set_tooltip(query_file)
            window['-QUERY-'].update(text)
            window['-OUTPUT-'].update('')
    return query_file

def save_file(window, query_file):
    if query_file:
        text = window['-QUERY-'].get()
        with open(query_file,'w') as f:
            f.write(text)
    else:
        save_file_as(window)

def save_file_as(window):
    query_file = sg.popup_get_file(
        'Save',
        no_window=True,
        save_as=True,
        file_types=(('.SQL files','*.sql'),('All files','*.*')))
    if query_file:
        text = window['-QUERY-'].get()
        with open(query_file,'w') as f:
            f.write(text)
            window['-QUERYNAME-'].update(os.path.basename(query_file))
            window['-QUERYNAME-'].set_tooltip(query_file)
    return query_file

def show_help(window, run_event):
    # Display help popup in approximate center of window
    popup_location = get_popup_location(window)
    sg.popup(
        'Enter a SQL command',
        f'Press {run_event} or F5 to run query',
        'Press Control-Q to quit',
        font=window.Font,
        title='Help',
        location=popup_location)

def show_about(window):
    popup_location = get_popup_location(window)
    sg.popup(
        'SnowQuery',
        'Created with:',
        '🐍 PySimpleGUI https://PySimpleGUI.org',
        '❄  Snowflake Connector for Python https://www.snowflake.com/',
        '❖  PrettyTable https://github.com/jazzband/prettytable',
        font=window.Font,
        title='About',
        location=popup_location)

def get_popup_location(window):
    window_location = window.current_location()
    window_size = window.size
    popup_location = (
        window_location[0] + int(window_size[0]/2),
        window_location[1] + int(window_size[1]/2))
        
    return popup_location

def run(window, query, cursor, run_event):
    window['-OUTPUT-'].update('')
    if query:
        # Execute query and return output
        query_error, output = run_query(cursor, query)
        if query_error:
            # Display error output
            window['-OUTPUT-'].print(
                output,
                colors=('red'))
        else:
            # Display query output
            window['-OUTPUT-'].print(output)
    else:
        show_help(window, run_event)

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

def build_database_tree(window, dcursor):
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
    dbs = get_metadata(dcursor, sql, fully_qualified=False)
    for db in dbs:
        # Add database to tree
        db_key = f'-{db}-'
        tree_data.Insert('',db_key,db,[])

        # Get database schemas
        sql = f'SHOW SCHEMAS IN DATABASE {db};'
        schemas = get_metadata(dcursor, sql, fully_qualified=False)
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
    for object_type in object_types:
        sql = f'SHOW {object_type} IN ACCOUNT;'
        schema_objects = get_metadata(dcursor, sql, fully_qualified=True)
        for db, schema, name in schema_objects:
            # Add schema object to tree
            object_type_key = f'-{db}.{schema}-{object_type}-'
            schema_object_key = f'-{db}.{schema}.{name}-'
            tree_data.Insert(object_type_key,schema_object_key,name,[])

        window['-TREE-'].update(values=tree_data)
                    
    window['-STATUSBAR-'].update(value='Ready')

def get_metadata(dcursor, sql, fully_qualified):
    dcursor.execute(sql)

    if 'FUNCTIONS' in sql.upper() or 'PROCEDURES' in sql.upper():
        dbname = 'catalog_name'
        filter = """ WHERE "is_builtin" = 'N'"""
    else:
        dbname = 'database_name'
        filter = None

    if fully_qualified:
        results_sql = f'SELECT "{dbname}", "schema_name", "name"'
    else:
        results_sql = 'SELECT "name"'
    results_sql += 'FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))'
    if filter:
        results_sql += """ WHERE "is_builtin" = 'N'"""
    
    dcursor.execute(results_sql)
    if fully_qualified:
        metadata = [
                [row[dbname],
                row['schema_name'],
                row['name']]
            for row in dcursor]
    else:
        metadata = [row['name'] for row in dcursor]
    return metadata

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
