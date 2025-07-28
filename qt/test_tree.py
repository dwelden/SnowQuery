from csv import DictReader
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem

app = QApplication()

schema_object_list = []
with open("snowtree.csv", "r") as f:
    reader = DictReader(f)
    schema_object_list = [row for row in reader]

model = QStandardItemModel()
root = model.invisibleRootItem()
node_dict = {}

for index, schema_object in enumerate(schema_object_list):
    parent = schema_object["parent"]
    name = schema_object["name"]
    formatted_name = schema_object["formatted_name"]
    object_type = schema_object["object_type"]
    node = QStandardItem(name)
    node.index = index
    node_dict[name] = (node, schema_object)
    if parent:
        parent_node = node_dict[parent][0]
    else:
        parent_node = root
    parent_node.appendRow(node)
    
tree_view = QTreeView()
tree_view.setModel(model)

tree_view.show()
app.exec()
