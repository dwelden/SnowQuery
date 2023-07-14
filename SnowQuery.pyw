import json
import os.path
import threading
from string import ascii_uppercase, digits
from sys import argv

import prettytable as pt
from psg_reskinner import reskin
import PySimpleGUI as sg
import snowflake.connector
from snowflake.connector import DictCursor

def show_window(cursor, dcursor):
    ''' Build window and execute event loop '''
    # Window theme settings
    SnowTheme = {
        'BACKGROUND': '#fcfcff',
        'TEXT': '#222222',
        'INPUT': '#ffffff',
        'TEXT_INPUT': '#29b5e8',
        'SCROLL': '#f8f8ff',
        'BUTTON': ('#29b5e8', '#ffffff'),
        'PROGRESS': ('#29b5e8', '#ffffff'),
        'BORDER': 1,
        'SLIDER_DEPTH': 0,
        'PROGRESS_DEPTH': 0}
    sg.theme_add_new('Snow', SnowTheme)
    sg.theme('Snow')
    UI_font = ("Segoe UI", 11)
    fixed_font = ('Consolas', 11)
    toggle_images = get_toggle_images()

    # Event labels
    run_event     = '▶'      #F5
    new_event     = 'New      Ctrl+N'
    open_event    = 'Open     Ctrl+O'
    save_event    = 'Save     Ctrl+S'
    save_as_event = 'Save As...'
    quit_event    = 'Quit     Ctrl+Q'
    help_event    = 'Help     F1'
    about_event   = 'About'
    refresh_event = '⟳'

    # Query file name and label
    query_file = None
    new_query = 'New Query'
    
    # Create the Window layout
    menu_def = [
        ['&File',
            ['&' + new_event,
             '&' + open_event,
             '&' + save_event,
             save_as_event.replace('A','&A'),
             '---',
             '&' + quit_event]],
        ['&Help',
            ['&' + help_event,
             '&' + about_event]]]
    query_context_menu = ['',
        ['Cut::Cut~-QUERY-',
         'Copy::Copy~-QUERY-',
         'Paste::Paste~-QUERY-',
         'Delete::Delete~-QUERY-',
         '---',
         'Select All::Select All~-QUERY-']]
    output_context_menu = ['',
        ['Copy::Copy~-OUTPUT-',
         'Select All::Select All~-OUTPUT-']]
    query_id_context_menu = ['',
        ['Copy::Copy~-QUERYID-',]]
    tree_context_menu = ['',
        ['Copy::Copy~-TREE-',
         'Paste name in query::Paste~-TREE-',
         '---',
         'Refresh::Refresh~-TREE-']]
    tree_data = sg.TreeData()
    left_column = sg.Column(
        [   [sg.Text('Databases'),sg.Push(),sg.Button(refresh_event,tooltip='Refresh')],
            [sg.Tree(data=tree_data,
                    headings=[],
                    auto_size_columns=True,
                    select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                    right_click_menu=tree_context_menu,
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
            sg.Button(
                image_data=toggle_images['light'],
                key='-TOGGLE-THEME-',
                button_color=(
                    sg.theme_background_color(),
                    sg.theme_background_color()),
                border_width=0,
                metadata=sg.theme(),
                tooltip='Toggle between light and dark themes'),
            sg.Button(run_event,tooltip='Run (F5)')],
           [sg.Multiline(
                size=(80,15),
                key='-QUERY-',
                right_click_menu=query_context_menu,
                font=fixed_font,
                expand_x=True,
                expand_y=True)],
           [sg.Text('Output')],
           [sg.Multiline(
                disabled=True,
                size=(80,15),
                key='-OUTPUT-',
                right_click_menu=output_context_menu,
                font=fixed_font,
                expand_x=True,
                expand_y=True)]],
        expand_x=True,
        expand_y=True)
    status_bars = [
        sg.Multiline(
            no_scrollbar=True,
            expand_x=True,
            key='-STATUSBAR-'),
        sg.Multiline(
            disabled=True,
            size=36,
            tooltip='Query ID (right-click to copy)',
            right_click_menu=query_id_context_menu,
            no_scrollbar=True,
            key='-QUERYID-'),
        sg.Multiline(
            disabled=True,
            size=12,
            tooltip='Query duration',
            justification='right',
            no_scrollbar=True,
            key='-QUERYDURATION-')]
    layout = [
        [sg.Menu(menu_def)],
        [left_column, right_column],
        [status_bars]]

    # Create the Window
    icon = get_icon()
    window = sg.Window(
        title='Snow Query',
        icon=icon,
        layout=layout,
        font=UI_font,
        resizable=True,
        finalize=True)
    tree = window['-TREE-']
    tree.Widget.configure(show='tree')
    window['-QUERY-'].set_focus()

    # Bind keys to events
    window.bind('<F5>', run_event)
    window.bind('<Control-n>', new_event)
    window.bind('<Control-o>', open_event)
    window.bind('<Control-s>', save_event)
    window.bind('<Control-q>', quit_event)
    window.bind('<F1>', help_event)

    # Store cursors in window metadata
    window_metadata = dict(cursor=cursor, dcursor=dcursor)
    window.metadata = window_metadata

    # Build database tree
    refresh_tree(window, '')

    # Event Loop to process "events"
    while True:             
        event, values = window.read()
        if event in (sg.WIN_CLOSED, quit_event):
            break
        elif event == '-TOGGLE-THEME-':
            toggle_theme(window, toggle_images)
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
        elif event == refresh_event:
            refresh_tree(window, '')
        elif event == run_event:
            query = values["-QUERY-"]
            run(window, query, run_event)
        elif (event in query_context_menu[1]
          or event in output_context_menu[1]):
            do_clipboard_operation(event, window)
        elif event in query_id_context_menu[1]:
            copy_query_id(event, window)
        elif event in tree_context_menu[1]:
            selection = values['-TREE-'][0]
            do_tree_operation(event, window, selection)

    window.close()
    del window

    return

def toggle_theme(window, toggle_images):
    ''' Toggle between light and dark themes '''
    toggle_theme = window['-TOGGLE-THEME-']
    theme = toggle_theme.metadata
    if theme == 'DarkGrey15':
        theme = 'Snow'
        toggle_image = toggle_images['light']
    else:
        theme = 'DarkGrey15'
        toggle_image = toggle_images['dark']
    reskin(window, theme, sg.theme, sg.LOOK_AND_FEEL_TABLE, True)
    toggle_theme.metadata = theme
    toggle_theme.update(image_data=toggle_image)

def do_tree_operation(event, window, value):
    ''' Execute tree context menu event'''
    if event in ('Copy::Copy~-TREE-','Paste name in query::Paste~-TREE-'):
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(value)
        if event == 'Paste name in query::Paste~-TREE-':
            window.write_event_value('Paste::Paste~-QUERY-', '')
    elif event == 'Refresh::Refresh~-TREE-':
        refresh_tree(window, value)

def do_clipboard_operation(event, window):
    ''' Execute multiline context event '''
    event, element = event.split('~')
    event = event.split(':',maxsplit=1)[0]
    element:sg.Multiline = window[element]

    if event == 'Select All':
        element.Widget.focus_set()
        element.Widget.selection_clear()
        element.Widget.tag_add('sel', '1.0', 'end')
    elif event == 'Copy':
        try:
            text = element.Widget.selection_get()
            window.TKroot.clipboard_clear()
            window.TKroot.clipboard_append(text)
        except:
            show_message(window, 'Nothing selected')
    elif event == 'Paste':
        element.Widget.insert(sg.tk.INSERT, window.TKroot.clipboard_get())
    elif event == 'Cut':
        try:
            text = element.Widget.selection_get()
            window.TKroot.clipboard_clear()
            window.TKroot.clipboard_append(text)
            element.Widget.delete("sel.first", "sel.last")
        except:
            show_message(window, 'Nothing selected')
    elif event == 'Delete':
        try:
            element.Widget.delete("sel.first", "sel.last")
        except:
            show_message(window, 'Nothing selected')

def copy_query_id(event, window):
    ''' Copy query id '''
    event, element = event.split('~')
    event = event.split(':',maxsplit=1)[0]
    element:sg.Multiline = window[element]

    # Select all
    element.Widget.focus_set()
    element.Widget.selection_clear()
    element.Widget.tag_add('sel', '1.0', 'end')
    # Copy
    try:
        text = element.Widget.selection_get()
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(text)
    except:
        show_message(window, 'Nothing selected')
    element.Widget.tag_remove('sel', '1.0', 'end')

def new_file(window, new_query):
    ''' Create a new query '''
    query_file = None
    window['-QUERYNAME-'].update(new_query)
    window['-QUERYNAME-'].set_tooltip(new_query)
    window['-QUERY-'].update('')
    window['-OUTPUT-'].update('')
    window['-QUERYID-'].update('')
    window['-QUERYDURATION-'].update('')
    return query_file

def open_file(window):
    ''' Open an existing query file '''
    query_file = sg.popup_get_file(
        'Open',
        no_window=True,
        file_types=(('.SQL files','*.sql'),('All files','*.*')))
    if query_file:
        with open(query_file,'r',encoding='utf-8') as f:
            text = f.read()
            window['-QUERYNAME-'].update(os.path.basename(query_file))
            window['-QUERYNAME-'].set_tooltip(query_file)
            window['-QUERY-'].update(text)
            window['-OUTPUT-'].update('')
            window['-QUERYID-'].update('')
            window['-QUERYDURATION-'].update('')
    return query_file

def save_file(window, query_file):
    ''' Save query to file '''
    if query_file:
        text = window['-QUERY-'].get()
        with open(query_file,'w',encoding='utf-8') as f:
            f.write(text)
    else:
        save_file_as(window)

def save_file_as(window):
    ''' Save query as file '''
    query_file = sg.popup_get_file(
        'Save',
        no_window=True,
        save_as=True,
        file_types=(('.SQL files','*.sql'),('All files','*.*')))
    if query_file:
        text = window['-QUERY-'].get()
        with open(query_file,'w',encoding='utf-8') as f:
            f.write(text)
            window['-QUERYNAME-'].update(os.path.basename(query_file))
            window['-QUERYNAME-'].set_tooltip(query_file)
    return query_file

def show_help(window, run_event):
    ''' Show Help popup '''
    # Display help popup in approximate center of window
    popup_location = get_popup_location(window)
    sg.popup(
        'Enter a SQL command',
        f'Press {run_event} or F5 to run query',
        'Press Control-Q to quit',
        font=window.Font,
        button_justification='centered',
        title='Help',
        location=popup_location)

def show_about(window):
    ''' Show About popup '''
    popup_location = get_popup_location(window)
    sg.popup(
        'SnowQuery',
        'Created with:',
        '🐍 PySimpleGUI https://PySimpleGUI.org',
        '❄  Snowflake Connector for Python https://www.snowflake.com/',
        '❖  PrettyTable https://github.com/jazzband/prettytable',
        '☯  Reskinner Plugin for PySimpleGUI https://github.com/definite-d/PSG_Reskinner',
        font=window.Font,
        button_justification='centered',
        title='About',
        location=popup_location)

def show_message(window, message):
    ''' Show message popup '''
    popup_location = get_popup_location(window)
    sg.popup(
        message,
        font=window.Font,
        button_justification='centered',
        location=popup_location)

def get_popup_location(window):
    ''' Calculate and return location for popup relative to window '''
    window_location = window.current_location()
    window_size = window.size
    popup_location = (
        window_location[0] + int(window_size[0]/2),
        window_location[1] + int(window_size[1]/2))
        
    return popup_location

def run(window, query, run_event):
    ''' Execute query and display output '''
    window['-OUTPUT-'].update('')
    window['-QUERYID-'].update('')
    window['-QUERYDURATION-'].update('')
    cursor = window.metadata['cursor']
    if query:
        # Execute query and return output
        query_error, output, query_details = submit_query(cursor, query)
        if query_error:
            # Display error output
            window['-OUTPUT-'].print(
                output,
                colors=('red'))
        else:
            # Display query output
            window['-OUTPUT-'].print(output)
            window['-QUERYID-'].update(query_details['query_id'])
            window['-QUERYDURATION-'].update(query_details['query_duration'])
    else:
        show_help(window, run_event)

def submit_query(cursor, query):
    ''' Submit query to Snowflake and return formatted output '''
    query_error = False
    query_details = {
        "query_id"       : '',
        "query_duration" : ''
    }
    try:
        cursor.execute(query)
        output = pt.from_db_cursor(cursor)

        # Format output as Markdown table using pretty table
        output.set_style(pt.MARKDOWN)
        output.align = "l"
        for column in cursor.description:
            if column.precision:
                output.align[column.name] = "r"

        query_details['query_id'] = cursor.sfqid
        query_details['query_duration'] = query_duration(cursor)
    except Exception as e:
        query_error = True
        output = e.__repr__()
    return((query_error, output, query_details))

def query_duration(cursor):
    ''' Get duration of last execute query '''
    query_id = cursor.sfqid
    sql = f"""
        select
            to_varchar(
                time_from_parts(0, 0, 0, total_elapsed_time * 1000000)
            ) as elapsed
        from table(information_schema.query_history())
        where query_id = '{query_id}'"""
    try:
        query_duration = cursor.execute(sql).fetchone()[0]
    except:
        query_duration = ''
    return query_duration

def refresh_tree(window, node_key):
    ''' Prune and rebuild tree under selected node '''
    tree_data = window['-TREE-'].TreeData
    node = get_node(tree_data, node_key)
    if node_key:
        status = 'Refreshing...'
        window['-STATUSBAR-'].update(value=status)
        prune(tree_data, node)
    else:
        status = 'Loading databases...'
        window['-STATUSBAR-'].update(value=status)
        tree_data = sg.TreeData()

    window['-TREE-'].update(values=tree_data)

    # Start thread to build database tree
    threading.Thread(
        target=build_tree,
        args=(window,tree_data,node),
        daemon=True
    ).start()

def get_node(tree_data, node_key):
    ''' Get node by key '''
    tree_dict = tree_data.tree_dict
    return tree_dict.get(node_key)

def prune(tree_data, node):
    ''' Delete all descendant nodes under selected node '''
    descendant_nodes = get_descendant_nodes(node, [])
    for parent_node, node in descendant_nodes:
        parent_node.children.remove(node)
        del tree_data.tree_dict[node.key]

def get_descendant_nodes(node, descendant_nodes):
    ''' Collect and return all descendant nodes of selected node '''
    for child in node.children:
        descendant_nodes.append([node, child])
        descendant_nodes = get_descendant_nodes(child, descendant_nodes)
    return descendant_nodes

def build_tree(window, tree_data, node):
    ''' Retrieve database metadata from Snowflake and build tree below node '''
    object_types = [
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
        'Sequences']

    # Get node level
    if node.key == '':
        node_level = 'Root'
    else:
        node_level = node.values[0]

    dcursor = window.metadata['dcursor']
    if node_level == 'Root':
        scope = 'ACCOUNT'
        get_databases(dcursor, tree_data, scope)
        get_schemas(dcursor, tree_data, scope, object_types)
        for object_type in object_types:
            get_schema_objects(dcursor, tree_data, object_type, object_types, scope)
    elif node_level == 'Database':
        scope = f'{node_level} {node.key}'
        get_schemas(dcursor, tree_data, scope, object_types)
        for object_type in object_types:
            get_schema_objects(dcursor, tree_data, object_type, object_types, scope)
    elif node_level == 'Schema':
        scope = f'{node_level} {node.key}'
        for object_type in object_types:
            get_schema_objects(dcursor, tree_data, object_type, object_types, scope)
    elif node_level in object_types:
        scope = f'Schema {node.parent}'
        get_schema_objects(dcursor, tree_data, node_level, object_types, scope)

    window['-TREE-'].update(values=tree_data)
    window['-STATUSBAR-'].update(value='Ready')

def get_databases(dcursor, tree_data, scope):
    ''' Get databases '''
    dbs = get_metadata(dcursor, 'Databases', scope)

    # Add databases to tree
    for db in dbs:
        db_key = format_identifier(db)
        tree_data.Insert('',db_key,db,['Database',])

def get_schemas(dcursor, tree_data, scope, object_types):
    ''' Get database schemas '''
    schemas = get_metadata(dcursor, 'Schemas', scope)

    # Add schemas to tree
    for db, schema in schemas:
        db_key = db
        schema_key = f'{format_identifier(db)}.{format_identifier(schema)}'
        tree_data.Insert(db_key,schema_key,schema,['Schema',])

def get_schema_objects(dcursor, tree_data, object_type, object_types, scope):
    ''' Get schema objects'''
    schema_objects = get_metadata(dcursor, object_type, scope)

    # Add schema objects to tree
    for db, schema, name in schema_objects:
        # Add schema object types to tree
        for obj_type in object_types:
            # INFORMATION_SCHEMA has only Views
            if schema == 'INFORMATION_SCHEMA' and obj_type != 'Views':
                continue
            formatted_db = f'{format_identifier(db)}'
            formatted_schema = f'{format_identifier(schema)}'
            obj_type_key = f'{formatted_db}.{formatted_schema}-{obj_type}'
            if not get_node(tree_data, obj_type_key):
                # Add schema object type to tree
                schema_key = f'{format_identifier(db)}.{format_identifier(schema)}'
                tree_data.Insert(schema_key,obj_type_key,obj_type,[obj_type,'',])

        formatted_db = f'{format_identifier(db)}'
        formatted_schema = f'{format_identifier(schema)}'
        formatted_name = f'{format_identifier(name)}'
        object_type_key = f'{formatted_db}.{formatted_schema}-{object_type}'
        schema_object_key = f'{formatted_db}.{formatted_schema}.{formatted_name}'
        tree_data.Insert(object_type_key,schema_object_key,name,['leaf',])

def format_identifier(id):
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

def get_metadata(dcursor, object_type, scope):
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
    dcursor.execute(query)

    # Extract and return results
    if object_type == 'Databases':
        metadata = [row['name'] for row in dcursor]
    elif object_type == 'Schemas':
        metadata = [
                [row[dbname],
                row['name']]
            for row in dcursor]
    else:
        metadata = [
                [row[dbname],
                row['schema_name'],
                row['name']]
            for row in dcursor]

    return metadata

def get_icon():
    ''' Get window icon '''
    icon = b'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'
    return icon

def get_toggle_images():
    ''' Get toggle theme button images '''
    toggle_images = {
        'dark': b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAF9SURBVFhH7ZdRToQwEEBnCcVl/eMOXIdE9kM9gnoDDsBV1I/1g+twDl21yOrUli0sDSR1lpr0JaS08PEyU6bDKkmSAzhMIEdn8YK2eEFbvKAtk3UwyzJ59/eEjMHLbidn4xgFr29uoW1b+HjfyxUaUBIxiZ4Iohjnn9BwLlfOgymaPUGU27+9ytkyDEW7j8QFOQQzl2+3ciYFp+TSNO1d1OjbS6T4Ks/hq2nk0hElUxSFGBVlWYqxrmsxUqBSvbq7fziMRQ/lhmJDUJRaMsBSMmSOHILvUKacsQgC6jpnA2b25KibGz0FdRR9s2DL/xPEsqHq3ByoS01wsY7lrXus4w0EP8jpkblRpI5e0/Dfow4P57H2SpWPYdlR8tSniDjqUHBOs6BDKaaoqkqMXT/oSruF6D1htwGfnx4h3lyKh0uiyyG9jlph2pOUsCiCMGQiUDqjggimHKFOO2YN/4H0qOkYBRWUv52I+hhMTAoujW8WbPGCtnhBWxwXBPgGhwinxwj3/s8AAAAASUVORK5CYII=',
        'light': b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAKpSURBVFhH7ZbPaxNBFMdnZjdZUZoeihakCJLaQympFCGlevTQBmpJD/0DPEoFDxIVFEIPBsUi0rv/QKAlKqmC4EXFRARTe/FXDiKKVoUa0GQ3O+N7yWzdbYgkcSIV9pNDdn5/eW/ee0N8fHx8fHY2VP43EE/e22dX7JnieGRJUBaAmUzIsb8FDhX4o5xb4Xxh3hQ0s5qKbchhDw0Cp05nDaOXJV5HIwuCMdinu6AAEEoGc88vmpvk2upSrFIfqeMReCKR2V88euQd1zRNNLVtd6BgCWbb1aHciwPLlyc/yu7fAmcT2YGXxw6DONYVabjpLo0SXe5eBUFlGz3thdlchB8+Hbh1deYDtmvTp5O3dxfHxkpgOYZtleCGoSAjj4/vrXdsY+L+BvlucsJlGwFL2sMPHvWkr8/9rAnSqtp5wdSLC4Iz1mP9TcUhOIZzAi7Hwd3XrD2hs/hN4xeW+15NjH/hEBAqwfPWp/plqzVGsp+2LMkgcIafrfUxTo04RqtqQoH298Sr4ACpjZiQ5uhI5n3Z1nVD9isBj0G3dYLbippVLTNQGpRtZRgQrZ3iXgueNUCgNxeqAIOjUzzBAtrUXz7FMMjgyquZyTvf0nKtRW0gkJuyrQysEJ3iXgs1usLCucI81kGV4HZYIdoF1zhSqBAEtJ1iTFRWwIqyWx1Yvtpl07UGBQYNLcNWUrNfB/NrC9ihEjxq9O7neqMFcK7beoeeFC6lk5PfalHMNesK+NuujSoELzwm3j+5G8dwjjs44EVjB36UFvF7K+n8q+eWkyMx0lt+bjns6AerAz75g73szJtoJAWlRnWAN4AC4HqJoVzhnK6XbqSTc56019ROYM0equvTb6OjN7Feqy6JmIQhe1QO5gsnqVW9Ay4tySEfHx8fn/8HQn4BR5shhwHpGZ8AAAAASUVORK5CYII='
    }
    return toggle_images

def main():
    ''' Establish connection to Snowflake and show window '''

    # Load Snowflake connection parameters
    scp_pathname = os.path.dirname(argv[0])     # same path as this script
    scp_filename = 'SnowflakeConnectionParameters.json'
    scp_file = os.path.join(scp_pathname, scp_filename)
    with open(scp_file, 'r') as scp:
        connection_parameters = json.load(scp)

    # Connect to Snowflake and create cursors
    with snowflake.connector.connect(**connection_parameters) as cnxn:
        with cnxn.cursor() as cursor, cnxn.cursor(DictCursor) as dcursor:

            # Show window and begin event loop
            show_window(cursor, dcursor)

if __name__ == '__main__':
    main()
