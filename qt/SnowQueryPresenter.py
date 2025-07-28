from PySide6.QtWidgets import QTreeWidgetItem

class Presenter:

    # Constants for node column positions
    NAME = 0
    PARENT = 1
    FORMATTED_NAME = 2
    OBJECT_TYPE = 3
    NODE_LEVEL = 3

    def __init__(self, model, view):
        ''' Connect presenter to model and view '''
        self.model = model
        self.view = view
        self.view.set_presenter(self)
        self.node_dict = {}

    def build_tree(self, node_level, scope):
        ''' Retrieve database metadata from Snowflake and build tree below node '''

        schema_object_list = self.model.get_schema_object_list(node_level, scope)

        # Create tree nodes and add to tree
        for schema_object in schema_object_list:
            name, parent, formatted_name, object_type = schema_object.values()
            if object_type == "object_header":
                node_level = name
            elif object_type in self.model.object_types:
                node_level = "leaf"
            else:
                node_level = object_type
            node = QTreeWidgetItem([
                name,
                parent,
                formatted_name,
                node_level
            ])
            
            # Save nodes for parent node lookup
            self.node_dict[formatted_name] = node
            if parent:
                self.node_dict[parent].addChild(node)
            else:
                self.view.tree.addTopLevelItem(node)

        # Send signal to UI to update status
        self.view.update_status.emit("Ready")

    def submit_query(self):
        ''' Submit query and return output '''

        query = self.view.query_box.toPlainText()
        if query:
            # Clear output values
            self.view.set_output_values(
                {
                    "OUTPUT": "",
                    "QUERYID": "",
                    "QUERYDURATION" : ""
                },
                False
            )

            # Execute query and return output
            output, query_details = self.model.run_query(query)

            # Display query output
            self.view.set_output_values(
                {
                    "OUTPUT": output,
                    "QUERYID": query_details['query_id'],
                    "QUERYDURATION" : query_details['query_duration']
                },
                query_details['query_error']
            )
        else:
            self.view.show_help()
