from base64 import b64decode
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk, StringVar
from tkinter.scrolledtext import ScrolledText

import sv_ttk

class Tooltip:
    ''' Tooltip class implementation from https://dnmtechs.com/displaying-tooltips-in-tkinter/ '''
    def __init__(self, widget, text):
        ''' Initialize tooltop widget'''
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        ''' Show tooltip '''
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() - 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#ffffe0",
            foreground="black",
            relief="solid",
            borderwidth=1
        )
        label.pack()

    def hide_tooltip(self, event):
        ''' Hide tooltip '''
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ContextMenu:
    def __init__(self, widget, entries):
        ''' Initialize context menu'''
        menu = tk.Menu(master=widget)
        for label, command in entries:
            if label:
                menu.add_command(label=label, command=command)
            else:
                menu.add_separator()
        if (widget.tk.call('tk', 'windowingsystem')=='aqua'):
            widget.bind('<2>', lambda e: menu.tk_popup(e.x_root, e.y_root))
            widget.bind('<Control-1>', lambda e: menu.tk_popup(e.x_root, e.y_root))
        else:
            widget.bind('<3>', lambda e: menu.tk_popup(e.x_root, e.y_root))

class View:
    def __init__(self):
        ''' Build window '''

        self.window = tk.Tk()
        self.window.title('Snow Query')

        # Window theme settings override
        self.snow_fg = "#29b5e8"
        self.light_img, self.dark_img = self.get_toggle_images()

        # set window icon
        icon = b64decode(self.get_icon())
        ico_file = tk.PhotoImage(data=icon)
        self.window.iconphoto(True, ico_file)

        # Create menus and bind accelerator keys
        self.window.option_add('*tearOff', False)
        menu_bar = tk.Menu(master=self.window)
        menu_file = tk.Menu(master=menu_bar)

        # File menu
        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New', underline=0, command=self.new_file)
        menu_file.entryconfigure('New', accelerator='Control-N')
        self.window.bind('<Control-n>', self.new_file)
        menu_file.add_command(label='Open...', underline=0, command=self.open_file)
        menu_file.entryconfigure('Open...', accelerator='Control-O')
        self.window.bind('<Control-o>', self.open_file)
        menu_file.add_command(label='Save', underline=0, command=self.save_file)
        menu_file.entryconfigure('Save', accelerator='Control-S')
        self.window.bind('<Control-s>', self.save_file)
        menu_file.add_command(label='Save As...', underline=5, command=self.save_file_as)
        menu_file.entryconfigure('Save As...', accelerator='Shift-Control-S')
        self.window.bind('<Shift-Control-s>', self.save_file_as)
        menu_file.add_separator()
        menu_file.add_command(label='Quit', underline=0, command=quit)
        menu_file.entryconfigure('Quit', accelerator='Control-Q')
        self.window.bind('<Control-q>', quit)

        # Help menu
        menu_help = tk.Menu(master=menu_bar, name='help')
        menu_bar.add_cascade(menu=menu_help, label='Help')
        menu_help.add_command(label='Help', underline=0, command=self.show_help)
        menu_help.entryconfigure('Help', accelerator='F1')
        self.window.bind('<F1>', self.show_help)
        menu_help.add_command(label='About', underline=0, command=self.show_about)
        self.window['menu'] = menu_bar

        # Create the Window layout
        main_box = ttk.Frame(master=self.window)
        main_pane = ttk.PanedWindow(master=main_box, orient='horizontal')
        left_column = ttk.Frame(master=main_pane)
        left_header = ttk.Frame(master=left_column)
        tree_label = ttk.Label(master=left_header, text="Databases")
        tree_label.pack(side='left', padx=5)
        self.refresh_button = tk.Button(
            master=left_header,
            fg=self.snow_fg,
            text="⟳",
            width=1
        )
        self.refresh_button.pack(side='right')
        refresh_button_tooltip = Tooltip(
            widget=self.refresh_button,
            text="Refresh"
        )
        left_header.pack(fill='both')
        self.tree = ttk.Treeview(master=left_column, selectmode='browse', show='tree')
        self.tree.column(column="#0", width=300)
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll_bar = tk.Scrollbar(master=left_column, command=self.tree.yview)
        tree_scroll_bar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=tree_scroll_bar.set)
        tree_scroll_bar.configure(command=self.tree.yview)
        tree_context_menu = ContextMenu(
            widget=self.tree,
            entries=(
                ('Copy', self.tree_selection_copy),
                ('Paste name in query', self.tree_selection_paste_in_query),
                (None, None),
                ('Refresh', self.refresh_tree_node)
            )
        )
        left_column.pack(side='left', fill='both')

        right_column = ttk.PanedWindow(master=main_pane, orient='vertical')
        right_header = ttk.Frame(master=right_column)
        self.query_label_var = StringVar()
        self.query_label = ttk.Label(
            master=right_header,
            textvariable=self.query_label_var
        )
        self.query_label.pack(side='left', padx=5)
        self.run_button = tk.Button(
            master=right_header,
            fg=self.snow_fg,
            text="▶",
            width=1
        )
        self.run_button.pack(side='right')
        run_button_tooltip = Tooltip(
            widget=self.run_button,
            text="Run (F5)"
        )

        self.toggle_theme_switch = tk.Button(
            master=right_header,
            bd=0,
            image=self.light_img,
            command=self.toggle_theme
        )
        self.toggle_theme_switch.pack(side='right')
        toggle_theme_switch_tooltip = Tooltip(
            widget=self.toggle_theme_switch,
            text="Toggle light &\ndark themes"
        )

        right_header.pack(fill='both')
        self.query_box = ScrolledText(
            master=right_column,
            relief='sunken',
            foreground=self.snow_fg
        )
        self.query_box.pack(fill='both')
        query_context_menu = ContextMenu(
            widget=self.query_box,
            entries=(
                ('Cut', self.cut_query_text),
                ('Copy', self.copy_query_text),
                ('Paste', self.paste_query_text),
                ('Delete', self.delete_query_text),
                (None, None),
                ('Select All', self.select_all_query_text)
            )
        )
        output_frame = ttk.Frame(master=right_column)
        output_label = ttk.Label(master=output_frame, text="Output")
        output_label.pack(anchor='w', padx=5)
        self.output_box = ScrolledText(
            master=output_frame,
            relief='sunken',
            state='disabled'
        )
        self.output_box.pack(fill='both', expand=True)
        output_context_menu = ContextMenu(
            widget=self.output_box,
            entries=(
                ('Copy', self.copy_output_text),
                ('Select All', self.select_all_output_text)
            )
        )
        output_frame.pack(fill='both', expand=True)
        right_column.add(right_header)
        right_column.add(self.query_box)
        right_column.add(output_frame)
        right_column.pack(side='right', fill='both')

        main_pane.add(left_column)
        main_pane.add(right_column)
        main_pane.pack(padx=5, pady=5, fill='both', expand=True)

        status_box = ttk.Frame(master=main_box)
        self.status_bar_var = StringVar()
        self.status_bar_var.set("Ready")
        status_bar = ttk.Entry(
            master=status_box,
            foreground=self.snow_fg,
            state='readonly',
            textvariable=self.status_bar_var
        )
        status_bar.pack(side='left', fill='x', expand=True)
        self.query_id_var = StringVar()
        self.query_id = ttk.Entry(
            master=status_box,
            width=36,
            foreground=self.snow_fg,
            state='readonly',
            textvariable=self.query_id_var
        )
        query_id_context_menu = ContextMenu(
            widget=self.query_id,
            entries=(
                ('Copy', self.copy_query_id),
            )
        )
        query_id_tooltip = Tooltip(
            widget=self.query_id,
            text="Query ID (right-click to copy)"
        )
        self.query_duration_var = StringVar()
        query_duration = ttk.Entry(
            master=status_box,
            width=12,
            foreground=self.snow_fg,
            state='readonly',
            textvariable=self.query_duration_var
        )
        query_duration.pack(side='right')
        query_duration_tooltip = Tooltip(
            widget=query_duration, 
            text="Query duration"
        )
        self.query_id.pack(side='right')
        status_box.pack(fill='x')
        main_box.pack(padx=5, pady=5, fill='both', expand=True)

        self.position_window()
        sv_ttk.set_theme("light")

        return

    def show(self):
        ''' Show window and begin main loop '''
        self.refresh_button.configure(command=self.presenter.refresh_tree
        )
        self.run_button.configure(command=self.presenter.submit_query)
        self.window.bind('<F5>', self.presenter.submit_query)
        self.presenter.refresh_tree()
        self.new_file()
        self.window.mainloop()

    def position_window(self):
        ''' Set initial size and position of main window '''
        # get the screen dimension
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Set size and position of window
        window_factor = .9
        window_width = int(window_factor * screen_width) #800
        window_height = int(window_factor * screen_height) #600

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def set_presenter(self, presenter):
        ''' Set presenter '''
        self.presenter = presenter

    def set_status_bar(self, status):
        ''' Set status bar '''
        self.status_bar_var.set(status)

    def set_output_values(self, output_values, error):
        ''' Output query results, query id, and query duration '''
        if error:
            self.output_box.config(fg="red")
        else:
            self.output_box.config(fg=self.snow_fg)
        output = output_values["OUTPUT"]
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", "end")
        self.output_box.insert(index="1.0", chars=output)
        self.output_box.config(state='disabled')
        self.query_id_var.set(output_values["QUERYID"])
        self.query_duration_var.set(output_values["QUERYDURATION"])

    def toggle_theme(self):
        ''' Toggle between light and dark themes '''
        sv_ttk.toggle_theme()
        if sv_ttk.get_theme() == "light":
            # Set light theme
            self.toggle_theme_switch.config(image=self.light_img)
        else:
            # Set dark theme
            self.toggle_theme_switch.config(image=self.dark_img)

    def refresh_tree_node(self):
        ''' Refresh tree under the selected node '''
        node = self.tree.selection()[0]
        self.presenter.refresh_tree(node=node)

    def tree_selection_copy(self):
        ''' Copy tree selection '''
        value = self.tree.selection()
        if value:
            self.window.clipboard_clear()
            self.window.clipboard_append(value[0])
        else:
            messagebox.showerror("Nothing selected")

    def tree_selection_paste_in_query(self):
        ''' Paste tree selection in query '''
        value = self.tree.selection()
        if value:
            self.query_box.insert(self.query_box.index(tk.INSERT), value[0])
        else:
            messagebox.showerror("Nothing selected")

    def cut_query_text(self):
        ''' Cut query text '''
        value = self.query_box.selection_get()
        if value:
            self.query_box.event_generate("<<Cut>>")
        else:
            messagebox.showerror("Nothing selected")

    def copy_query_text(self):
        ''' Copy query text '''
        value = self.query_box.selection_get()
        if value:
            self.query_box.event_generate("<<Copy>>")
        else:
            messagebox.showerror("Nothing selected")

    def paste_query_text(self):
        ''' Paste text in query '''
        value = self.window.clipboard_get()
        if value:
            self.query_box.insert(
                index=self.query_box.index(tk.INSERT),
                chars=value
            )
        else:
            messagebox.showerror("Nothing to paste")

    def delete_query_text(self):
        ''' Delete query text '''
        value = self.query_box.selection_get()
        if value:
            self.query_box.delete("sel.first", "sel.last")
        else:
            messagebox.showerror("Nothing selected")

    def select_all_query_text(self):
        ''' Select all query text '''
        self.query_box.focus_set()
        self.query_box.selection_clear()
        self.query_box.tag_add('sel', '1.0', 'end')

    def copy_output_text(self):
        ''' Copy output text '''
        value = self.output_box.selection_get()
        if value:
            self.output_box.event_generate("<<Copy>>")
        else:
            messagebox.showerror("Nothing selected")

    def select_all_output_text(self):
        ''' Select all output text '''
        self.output_box.focus_set()
        self.output_box.selection_clear()
        self.output_box.tag_add('sel', '1.0', 'end')

    def copy_query_id(self):
        ''' Copy query id '''
        self.query_id.select_range(0,'end')
        self.query_id.event_generate("<<Copy>>")

    def new_file(self):
        ''' Create a new query '''
        # Query file name and label
        self.query_file = None
        self.query_label_var.set("New Query")
        self.query_box.delete("1.0", "end")
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", "end")
        self.output_box.config(state='disabled')
        self.query_id_var.set("")
        self.query_duration_var.set("")

    def open_file(self):
        ''' Open an existing query file '''
        self.query_file = filedialog.askopenfilename(
            title="Open",
            filetypes=(("SQL Files", "*.sql"), ("All Files", "*.*")),
            initialdir="~"
        )
        if self.query_file:
            text = Path(self.query_file).read_text()
            self.query_label_var.set(Path(self.query_file).name)
            query_label_tooltip = Tooltip(
                widget=self.query_label,
                text=Path(self.query_file)
            )
            self.query_box.delete("1.0", "end")
            self.query_box.insert(
                index="1.0",
                chars=text)
            self.output_box.config(state='normal')
            self.output_box.delete("1.0", "end")
            self.output_box.config(state='disabled')
            self.query_id_var.set("")
            self.query_duration_var.set("")

    def save_file(self):
        ''' Save query to file '''
        if self.query_file:
            text = self.query_box.get("1.0", "end")
            Path(self.query_file).write_text(text)
        else:
            self.save_file_as()

    def save_file_as(self):
        ''' Save query to file '''
        if self.query_file:
            save_as_file_name = Path(self.query_file).name
        else:
            save_as_file_name = ""
        save_as_file_name = filedialog.asksaveasfilename(
            title="Save",
            confirmoverwrite=True,
            defaultextension=".sql",
            filetypes=(('.SQL files','*.sql'),('All files','*.*')),
            initialdir="~",
            initialfile=save_as_file_name
        )
        if save_as_file_name:
            self.query_file = save_as_file_name
            text = self.query_box.get("1.0", "end")
            Path(self.query_file).write_text(text)
            self.query_label_var.set(Path(self.query_file).name)
            query_label_tooltip = Tooltip(
                widget=self.query_label,
                text=Path(self.query_file)
            )

    def show_help(self):
        ''' Show Help popup '''
        help = """
        Enter a SQL command
        Press ▶ or F5 to run query
        Press Control-Q to quit
        """
        messagebox.showinfo(title="Help", message=help)

    def show_about(self):
        ''' Show About popup '''
        message = "Snow Query"
        detail = """
        Created with:
        🐍 Tkinter https://docs.python.org/3/library/tkinter.html
        ❄  Snowflake Connector for Python https://www.snowflake.com/
        ❖  PrettyTable https://github.com/jazzband/prettytable
        ☯  Sun Valley ttk Theme https://github.com/rdbende/Sun-Valley-ttk-theme
        """
        messagebox.showinfo(title="About", message=message, detail=detail)

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
        light_img = tk.PhotoImage(data=b64decode(toggle_images["light"]))
        dark_img = tk.PhotoImage(data=b64decode(toggle_images["dark"]))
        return light_img, dark_img
