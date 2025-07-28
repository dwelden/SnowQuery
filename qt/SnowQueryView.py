from pathlib import Path
import threading

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow, 
    QMenu,
    QMessageBox
)
from PySide6.QtGui import (
    QAction,
    QClipboard
)
from PySide6.QtCore import (
    QDir,
    Qt,
    Signal,
    Slot
)
from SnowQueryUI import Ui_MainWindow

# TODO:
# Theme toggle

class View(QMainWindow, Ui_MainWindow):
    update_status = Signal(str)

    def __init__(self):
        ''' Build window '''
        self.app = QApplication()
        super().__init__()
        self.setupUi(self)
        self.update_status.connect(self.set_status)
        
        # Configure tree
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels([
            "Name",
            "Parent",
            "Formatted Name",
            "Node Level"
        ])
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)

        # Load stylesheets
        self.light_stylesheet = Path("light.qss").read_text()
        self.dark_stylesheet = Path("dark.qss").read_text()
        
    def apply_theme(self, theme):
        match theme:
            case "light":
                self.setStyleSheet(self.light_stylesheet)
            case "dark":
                self.setStyleSheet(self.dark_stylesheet)

        # Save default theme text color
        self.theme_text_color = self.output_box.textColor()

    def show(self):
        ''' Show window and begin main loop '''
        self.refresh_tree()
        self.new_file()

        # Connect signals and slots for File menu
        self.actionNew.triggered.connect(self.new_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionSave_As.triggered.connect(self.save_file_as)
        self.actionQuit.triggered.connect(self.app.quit)

        # Connect signals and slots for Help menu
        self.actionHelp.triggered.connect(self.show_help)
        self.actionAbout.triggered.connect(self.show_about)

        # Connect signals and slots for buttons
        self.refresh_button.clicked.connect(self.refresh_tree)
        self.run_button.clicked.connect(self.presenter.submit_query)
        self.theme_switch.stateChanged.connect(self.toggle_theme)

        # Connect signals and slots tree context menu
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)

        # Default to dark theme
        self.apply_theme("dark")

        super().show()
        self.app.exec()

    def set_presenter(self, presenter):
        ''' Set presenter '''
        self.presenter = presenter

    def set_status(self, status):
        ''' Set status '''
        self.status.setText(status)

    def set_output_values(self, output_values, error):
        ''' Output query results, query id, and query duration '''
        if error:
            self.output_box.setTextColor("red")
        else:
            self.output_box.setTextColor(self.theme_text_color)
        self.output_box.clear()
        self.output_box.setText(output_values["OUTPUT"])
        self.query_id.setText(output_values["QUERYID"])
        self.query_duration.setText(output_values["QUERYDURATION"])

    @Slot()
    def toggle_theme(self):
        ''' Toggle between light and dark themes '''
        if self.theme_switch.checkState() == Qt.CheckState.Checked:
            # Set light theme
            self.apply_theme("light")
        else:
            # Set dark theme
            self.apply_theme("dark")

    @Slot()
    def show_tree_context_menu(self, position):
        menu = QMenu(self.tree)

        # Copy formatted node name to clipboard
        copy_node_action = QAction("Copy")
        copy_node_action.triggered.connect(self.tree_selection_copy)
        menu.addAction(copy_node_action)
        
        # Paste formatted node name to query
        paste_node_action = QAction("Paste name in query")
        paste_node_action.triggered.connect(self.tree_selection_paste_in_query)
        menu.addAction(paste_node_action)
        
        menu.addSeparator()
        
        # Refresh tree under node
        refresh_node_action = QAction("Refresh")
        refresh_node_action.triggered.connect(self.refresh_tree_node)
        menu.addAction(refresh_node_action)

        menu.exec_(self.tree.mapToGlobal(position))

    @Slot()
    def tree_selection_copy(self):
        ''' Copy tree selection '''
        value = self.tree.currentItem().text(self.presenter.FORMATTED_NAME)
        if value:
            clipboard = QApplication.clipboard()
            clipboard.clear()
            clipboard.setText(value)
        else:
            self.show_error("Nothing selected")

    @Slot()
    def tree_selection_paste_in_query(self):
        ''' Paste tree selection in query '''
        value = self.tree.currentItem().text(self.presenter.FORMATTED_NAME)
        if value:
            self.query_box.insertPlainText(value)
        else:
            self.show_error("Nothing selected")

    @Slot()
    def refresh_tree_node(self):
        ''' Refresh tree under the selected node '''
        node = self.tree.currentItem()
        self.refresh_tree(node=node)

    @Slot()
    def refresh_tree(self, node=None):
        ''' Prune and rebuild tree '''
        # Get node level
        if not node:
            node_level = "Root"
        else:
            node_parent = node.text(self.presenter.PARENT)
            node_formatted_name = node.text(self.presenter.FORMATTED_NAME)
            node_level = node.text(self.presenter.NODE_LEVEL)
        
        # Determine scope and get schema object list
        scope = ""
        if node_level == "Root":
            scope = "ACCOUNT"
        elif node_level in ("Database", "Schema"):
            scope = f"{node_level} {node_formatted_name}"
        elif node_level != "leaf":
            scope = f"Schema {node_parent}"

        # Continue if valid scope identified
        if scope:
            if node:
                # Prune node children
                status = "Refreshing..."
                node.takeChildren()
            else:
                # Clear tree
                status = "Loading databases..."
                self.tree.clear()

            self.set_status(status)

            # Start thread to build database tree
            threading.Thread(
                target=self.presenter.build_tree,
                args=(node_level, scope),
                daemon=True
            ).start()

    @Slot()
    def new_file(self):
        ''' Create a new query '''
        # Query file name and label
        self.query_file = None
        self.query_label.setText("New Query")
        self.query_box.clear()
        self.output_box.clear()
        self.query_id.setText("")
        self.query_duration.setText("")

    @Slot()
    def open_file(self):
        ''' Open an existing query file '''
        self.query_file = QFileDialog.getOpenFileName(
            caption="Open file",
            dir=QDir.homePath(),
            filter="SQL files (*.sql);;All files (*.*)"
        )[0]
        if self.query_file:
            text = Path(self.query_file).read_text()
            self.query_label.setText(Path(self.query_file).name)
            self.query_label.setToolTip(self.query_file)
            self.query_box.clear()
            self.query_box.setPlainText(text)
            self.output_box.clear()
            self.query_id.setText("")
            self.query_duration.setText("")

    @Slot()
    def save_file(self):
        ''' Save query to file '''
        if self.query_file:
            text = self.query_box.toPlainText()
            Path(self.query_file).write_text(text)
        else:
            self.save_file_as()

    @Slot()
    def save_file_as(self):
        ''' Save query to file '''
        if self.query_file:
            save_as_file_name = Path(self.query_file).name
        else:
            save_as_file_name = ""
        save_as_file_name = QFileDialog.getSaveFileName(
            caption="Save file",
            dir=QDir.homePath(),
            filter="SQL files (*.sql);;All files (*.*)"
        )[0]
        if save_as_file_name:
            self.query_file = save_as_file_name
            text = self.query_box.toPlainText()
            Path(self.query_file).write_text(text)
            self.query_label.setText(Path(self.query_file).name)
            self.query_label.setToolTip(Path(self.query_file))

    @Slot()
    def show_help(self):
        ''' Show Help popup '''
        help_message = QMessageBox.information(
            self,
            "Help",
            """
                Enter a SQL command

                Press ▶ or F5 to run query

                Press Control-Q to quit
            """
        )

    @Slot()
    def show_about(self):
        ''' Show About popup '''
        about_message = QMessageBox.about(
            self,
            "About Snow Query",
            """
                <b><h3>Snow Query</h3></b><br>
                Created with:<br>
                <table>
                <tr><td>🐍</td><td>Qt for Python</td><td>https://doc.qt.io/qtforpython-6/</td></tr>
                <tr><td>❄</td><td>Snowflake Connector for Python</td><td>https://www.snowflake.com/</td></tr>
                <tr><td>❖</td><td>PrettyTable</td><td>https://github.com/jazzband/prettytable</td></tr>
                </table>
            """
        )

    @Slot()
    def show_error(self, error_text):
        ''' Show Error popup '''
        error_message = QMessageBox.warning(
            self,
            "Error",
            error_text
        )
