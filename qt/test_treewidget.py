from csv import DictReader
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem

app = QApplication()

schema_object_list = []
with open("snowtree.csv", "r") as f:
    reader = DictReader(f)
    schema_object_list = [row for row in reader]

tree = QTreeWidget()
tree.setColumnCount(4)
tree.setHeaderLabels([
    "Name",
    "Parent",
    "Formatted Name",
    "Object Type"
])
tree.hideColumn(1)
tree.hideColumn(2)
tree.hideColumn(3)

node_dict = {}

for index, schema_object in enumerate(schema_object_list):
    name = schema_object["name"]
    parent = schema_object["parent"]
    node = QTreeWidgetItem(schema_object.values())
    node_dict[name] = node
    if parent:
        node_dict[parent].addChild(node)
    else:
        tree.addTopLevelItem(node)

tree.show()
app.exec()
