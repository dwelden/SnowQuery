import os.path
import threading

from psg_reskinner import reskin
import PySimpleGUI as sg

class View:
    def __init__(self):
        ''' Build window '''
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
        self.toggle_images = self.get_toggle_images()

        # Event labels
        self.run_event     = '▶'      #F5
        self.new_event     = 'New      Ctrl+N'
        self.open_event    = 'Open     Ctrl+O'
        self.save_event    = 'Save     Ctrl+S'
        self.save_as_event = 'Save As...'
        self.quit_event    = 'Quit     Ctrl+Q'
        self.help_event    = 'Help     F1'
        self.about_event   = 'About'
        self.refresh_event = '⟳'

        # Query file name and label
        self.query_file = None
        self.new_query = 'New Query'
        
        # Create the Window layout
        self.menu_def = [
            ['&File',
                ['&' + self.new_event,
                '&' + self.open_event,
                '&' + self.save_event,
                self.save_as_event.replace('A','&A'),
                '---',
                '&' + self.quit_event]],
            ['&Help',
                ['&' + self.help_event,
                '&' + self.about_event]]]
        self.query_context_menu = ['',
            ['Cut::Cut~-QUERY-',
            'Copy::Copy~-QUERY-',
            'Paste::Paste~-QUERY-',
            'Delete::Delete~-QUERY-',
            '---',
            'Select All::Select All~-QUERY-']]
        self.output_context_menu = ['',
            ['Copy::Copy~-OUTPUT-',
            'Select All::Select All~-OUTPUT-']]
        self.query_id_context_menu = ['',
            ['Copy::Copy~-QUERYID-',]]
        self.tree_context_menu = ['',
            ['Copy::Copy~-TREE-',
            'Paste name in query::Paste~-TREE-',
            '---',
            'Refresh::Refresh~-TREE-']]
        left_column = sg.Column(
            [   [sg.Text('Databases'),sg.Push(),sg.Button(self.refresh_event,tooltip='Refresh')],
                [sg.Tree(data=sg.TreeData(),
                        headings=[],
                        auto_size_columns=True,
                        select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                        right_click_menu=self.tree_context_menu,
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
            [  [sg.Text(self.new_query,key='-QUERYNAME-'),
                sg.Push(),
                sg.Button(
                    image_data=self.toggle_images['light'],
                    key='-TOGGLE-THEME-',
                    button_color=(
                        sg.theme_background_color(),
                        sg.theme_background_color()),
                    border_width=0,
                    metadata=sg.theme(),
                    tooltip='Toggle between light and dark themes'),
                sg.Button(self.run_event,tooltip='Run (F5)')],
            [sg.Multiline(
                    size=(80,15),
                    key='-QUERY-',
                    right_click_menu=self.query_context_menu,
                    font=fixed_font,
                    expand_x=True,
                    expand_y=True)],
            [sg.Text('Output')],
            [sg.Multiline(
                    disabled=True,
                    size=(80,15),
                    key='-OUTPUT-',
                    right_click_menu=self.output_context_menu,
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
                right_click_menu=self.query_id_context_menu,
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
            [sg.Menu(self.menu_def)],
            [left_column, right_column],
            [status_bars]]

        # Create the Window
        icon = self.get_icon()
        self.window = sg.Window(
            title='Snow Query',
            icon=icon,
            layout=layout,
            font=UI_font,
            resizable=True,
            finalize=True)
        tree = self.window['-TREE-']
        tree.Widget.configure(show='tree')
        self.window['-QUERY-'].set_focus()

        # Bind keys to events
        self.window.bind('<F5>', self.run_event)
        self.window.bind('<Control-n>', self.new_event)
        self.window.bind('<Control-o>', self.open_event)
        self.window.bind('<Control-s>', self.save_event)
        self.window.bind('<Control-q>', self.quit_event)
        self.window.bind('<F1>', self.help_event)

        return

    def set_presenter(self, presenter):
        self.presenter = presenter

    def set_tree_data(self, tree_data):
        self.window['-TREE-'].update(values=tree_data)

    def get_tree_data(self):
        return self.window['-TREE-'].TreeData
    
    def set_status_bar(self, status):
        self.window['-STATUSBAR-'].update(value=status)

    def set_output_values(self, output_values, error):
        for key, value in output_values.items():
            if key == "-OUTPUT-":
                if not value:
                    self.window[key].update(value)
                elif error:
                    self.window[key].print(value, colors="red")
                else:
                    self.window[key].print(value)
            else:
                self.window[key].update(value)

    def show(self):
        ''' Show window and execute event loop '''

        # Build database tree
        self.refresh_tree('')

        # Event Loop to process "events"
        while True:             
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, self.quit_event):
                break
            elif event == '-TOGGLE-THEME-':
                self.toggle_theme()
            elif event == '-TREE-':
                continue
            elif event == self.new_event:
                query_file = self.new_file()
            elif event == self.open_event:
                query_file = self.open_file()
            elif event == self.save_event:
                self.save_file()
            elif event == self.save_as_event:
                query_file = self.save_file_as()
            elif event == self.help_event:
                self.show_help()
            elif event == self.about_event:
                self.show_about()
            elif event == self.refresh_event:
                self.refresh_tree('')
            elif event == self.run_event:
                query = values["-QUERY-"]
                self.presenter.submit_query(query)
            elif (event in self.query_context_menu[1]
            or event in self.output_context_menu[1]):
                self.do_clipboard_operation(event)
            elif event in self.query_id_context_menu[1]:
                self.copy_query_id(event)
            elif event in self.tree_context_menu[1]:
                selection = values['-TREE-'][0]
                self.do_tree_operation(event, selection)

        self.window.close()
        del self.window

        return

    def toggle_theme(self):
        ''' Toggle between light and dark themes '''
        toggle_theme = self.window['-TOGGLE-THEME-']
        theme = toggle_theme.metadata
        if theme == 'DarkGrey15':
            theme = 'Snow'
            toggle_image = self.toggle_images['light']
        else:
            theme = 'DarkGrey15'
            toggle_image = self.toggle_images['dark']
        reskin(self.window, theme, sg.theme, sg.LOOK_AND_FEEL_TABLE, True)
        toggle_theme.metadata = theme
        toggle_theme.update(image_data=toggle_image)

    def do_tree_operation(self, event, value):
        ''' Execute tree context menu event'''
        if event in ('Copy::Copy~-TREE-','Paste name in query::Paste~-TREE-'):
            self.window.TKroot.clipboard_clear()
            self.window.TKroot.clipboard_append(value)
            if event == 'Paste name in query::Paste~-TREE-':
                self.window.write_event_value('Paste::Paste~-QUERY-', '')
        elif event == 'Refresh::Refresh~-TREE-':
            self.refresh_tree(value)

    def refresh_tree(self, node_key):
        ''' Prune and rebuild tree under selected node '''
        tree_data = self.get_tree_data()
        node = tree_data.tree_dict.get(node_key)

        # Get node level
        if node.key == '':
            node_level = 'Root'
        else:
            node_level = node.values[0]

        # Determine scope and get schema object list
        scope = ""
        if node_level == "Root":
            scope = "ACCOUNT"
        elif node_level in ("Database", "Schema"):
            scope = f"{node_level} {node.key}"
        elif node_level != "leaf":
            scope = f"Schema {node.parent}"

        # Continue if valid scope identified
        if scope:
            if node_key:
                status = 'Refreshing...'
                self.prune(tree_data, node)
            else:
                status = 'Loading databases...'
                tree_data = sg.TreeData()
                self.set_tree_data(tree_data)

            self.set_status_bar(status)

            # Start thread to build database tree
            threading.Thread(
                target=self.presenter.build_tree,
                args=(tree_data, node_level, scope),
                daemon=True
            ).start()

    def prune(self, tree_data, node):
        ''' Delete all descendant nodes under selected node '''
        descendant_nodes = self.get_descendant_nodes(node, [])
        for parent_node, node in descendant_nodes:
            parent_node.children.remove(node)
            del tree_data.tree_dict[node.key]

    def get_descendant_nodes(self, node, descendant_nodes):
        ''' Collect and return all descendant nodes of selected node '''
        for child in node.children:
            descendant_nodes.append([node, child])
            descendant_nodes = self.get_descendant_nodes(child, descendant_nodes)
        return descendant_nodes

    def do_clipboard_operation(self, event):
        ''' Execute multiline context event '''
        event, element = event.split('~')
        event = event.split(':',maxsplit=1)[0]
        element:sg.Multiline = self.window[element]

        if event == 'Select All':
            element.Widget.focus_set()
            element.Widget.selection_clear()
            element.Widget.tag_add('sel', '1.0', 'end')
        elif event == 'Copy':
            try:
                text = element.Widget.selection_get()
                self.window.TKroot.clipboard_clear()
                self.window.TKroot.clipboard_append(text)
            except:
                self.show_message('Nothing selected')
        elif event == 'Paste':
            element.Widget.insert(sg.tk.INSERT, self.window.TKroot.clipboard_get())
        elif event == 'Cut':
            try:
                text = element.Widget.selection_get()
                self.window.TKroot.clipboard_clear()
                self.window.TKroot.clipboard_append(text)
                element.Widget.delete("sel.first", "sel.last")
            except:
                self.show_message('Nothing selected')
        elif event == 'Delete':
            try:
                element.Widget.delete("sel.first", "sel.last")
            except:
                self.show_message('Nothing selected')

    def copy_query_id(self, event):
        ''' Copy query id '''
        event, element = event.split('~')
        event = event.split(':',maxsplit=1)[0]
        element:sg.Multiline = self.window[element]

        # Select all
        element.Widget.focus_set()
        element.Widget.selection_clear()
        element.Widget.tag_add('sel', '1.0', 'end')
        # Copy
        try:
            text = element.Widget.selection_get()
            self.window.TKroot.clipboard_clear()
            self.window.TKroot.clipboard_append(text)
        except:
            self.show_message('Nothing selected')
        element.Widget.tag_remove('sel', '1.0', 'end')

    def new_file(self):
        ''' Create a new query '''
        query_file = None
        self.window['-QUERYNAME-'].update(self.new_query)
        self.window['-QUERYNAME-'].set_tooltip(self.new_query)
        self.window['-QUERY-'].update('')
        self.window['-OUTPUT-'].update('')
        self.window['-QUERYID-'].update('')
        self.window['-QUERYDURATION-'].update('')
        return query_file

    def open_file(self):
        ''' Open an existing query file '''
        query_file = sg.popup_get_file(
            'Open',
            no_window=True,
            file_types=(('.SQL files','*.sql'),('All files','*.*')))
        if query_file:
            with open(query_file,'r',encoding='utf-8') as f:
                text = f.read()
                self.window['-QUERYNAME-'].update(os.path.basename(query_file))
                self.window['-QUERYNAME-'].set_tooltip(query_file)
                self.window['-QUERY-'].update(text)
                self.window['-OUTPUT-'].update('')
                self.window['-QUERYID-'].update('')
                self.window['-QUERYDURATION-'].update('')
        return query_file

    def save_file(self):
        ''' Save query to file '''
        if self.query_file:
            text = self.window['-QUERY-'].get()
            with open(self.query_file,'w',encoding='utf-8') as f:
                f.write(text)
        else:
            self.save_file_as()

    def save_file_as(self):
        ''' Save query as file '''
        query_file = sg.popup_get_file(
            'Save',
            no_window=True,
            save_as=True,
            file_types=(('.SQL files','*.sql'),('All files','*.*')))
        if query_file:
            text = self.window['-QUERY-'].get()
            with open(query_file,'w',encoding='utf-8') as f:
                f.write(text)
                self.window['-QUERYNAME-'].update(os.path.basename(query_file))
                self.window['-QUERYNAME-'].set_tooltip(query_file)
        return query_file

    def show_help(self):
        ''' Show Help popup '''
        # Display help popup in approximate center of window
        popup_location = self.get_popup_location()
        sg.popup(
            'Enter a SQL command',
            f'Press {self.run_event} or F5 to run query',
            'Press Control-Q to quit',
            font=self.window.Font,
            button_justification='centered',
            title='Help',
            location=popup_location)

    def show_about(self):
        ''' Show About popup '''
        popup_location = self.get_popup_location()
        sg.popup(
            'SnowQuery',
            'Created with:',
            '🐍 PySimpleGUI https://PySimpleGUI.org',
            '❄  Snowflake Connector for Python https://www.snowflake.com/',
            '❖  PrettyTable https://github.com/jazzband/prettytable',
            '☯  Reskinner Plugin for PySimpleGUI https://github.com/definite-d/PSG_Reskinner',
            font=self.window.Font,
            button_justification='centered',
            title='About',
            location=popup_location)

    def show_message(self, message):
        ''' Show message popup '''
        popup_location = self.get_popup_location()
        sg.popup(
            message,
            font=self.window.Font,
            button_justification='centered',
            location=popup_location)

    def get_popup_location(self):
        ''' Calculate and return location for popup relative to window '''
        window_location = self.window.current_location()
        window_size = self.window.size
        popup_location = (
            window_location[0] + int(window_size[0]/2),
            window_location[1] + int(window_size[1]/2))
            
        return popup_location

    def get_icon(self):
        ''' Get window icon '''
        icon = b'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'
        return icon

    def get_toggle_images(self):
        ''' Get toggle theme button images '''
        toggle_images = {
            'dark': b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAF9SURBVFhH7ZdRToQwEEBnCcVl/eMOXIdE9kM9gnoDDsBV1I/1g+twDl21yOrUli0sDSR1lpr0JaS08PEyU6bDKkmSAzhMIEdn8YK2eEFbvKAtk3UwyzJ59/eEjMHLbidn4xgFr29uoW1b+HjfyxUaUBIxiZ4Iohjnn9BwLlfOgymaPUGU27+9ytkyDEW7j8QFOQQzl2+3ciYFp+TSNO1d1OjbS6T4Ks/hq2nk0hElUxSFGBVlWYqxrmsxUqBSvbq7fziMRQ/lhmJDUJRaMsBSMmSOHILvUKacsQgC6jpnA2b25KibGz0FdRR9s2DL/xPEsqHq3ByoS01wsY7lrXus4w0EP8jpkblRpI5e0/Dfow4P57H2SpWPYdlR8tSniDjqUHBOs6BDKaaoqkqMXT/oSruF6D1htwGfnx4h3lyKh0uiyyG9jlph2pOUsCiCMGQiUDqjggimHKFOO2YN/4H0qOkYBRWUv52I+hhMTAoujW8WbPGCtnhBWxwXBPgGhwinxwj3/s8AAAAASUVORK5CYII=',
            'light': b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAKpSURBVFhH7ZbPaxNBFMdnZjdZUZoeihakCJLaQympFCGlevTQBmpJD/0DPEoFDxIVFEIPBsUi0rv/QKAlKqmC4EXFRARTe/FXDiKKVoUa0GQ3O+N7yWzdbYgkcSIV9pNDdn5/eW/ee0N8fHx8fHY2VP43EE/e22dX7JnieGRJUBaAmUzIsb8FDhX4o5xb4Xxh3hQ0s5qKbchhDw0Cp05nDaOXJV5HIwuCMdinu6AAEEoGc88vmpvk2upSrFIfqeMReCKR2V88euQd1zRNNLVtd6BgCWbb1aHciwPLlyc/yu7fAmcT2YGXxw6DONYVabjpLo0SXe5eBUFlGz3thdlchB8+Hbh1deYDtmvTp5O3dxfHxkpgOYZtleCGoSAjj4/vrXdsY+L+BvlucsJlGwFL2sMPHvWkr8/9rAnSqtp5wdSLC4Iz1mP9TcUhOIZzAi7Hwd3XrD2hs/hN4xeW+15NjH/hEBAqwfPWp/plqzVGsp+2LMkgcIafrfUxTo04RqtqQoH298Sr4ACpjZiQ5uhI5n3Z1nVD9isBj0G3dYLbippVLTNQGpRtZRgQrZ3iXgueNUCgNxeqAIOjUzzBAtrUXz7FMMjgyquZyTvf0nKtRW0gkJuyrQysEJ3iXgs1usLCucI81kGV4HZYIdoF1zhSqBAEtJ1iTFRWwIqyWx1Yvtpl07UGBQYNLcNWUrNfB/NrC9ihEjxq9O7neqMFcK7beoeeFC6lk5PfalHMNesK+NuujSoELzwm3j+5G8dwjjs44EVjB36UFvF7K+n8q+eWkyMx0lt+bjns6AerAz75g73szJtoJAWlRnWAN4AC4HqJoVzhnK6XbqSTc56019ROYM0equvTb6OjN7Feqy6JmIQhe1QO5gsnqVW9Ay4tySEfHx8fn/8HQn4BR5shhwHpGZ8AAAAASUVORK5CYII='
        }
        return toggle_images
