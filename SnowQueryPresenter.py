class Presenter:
    def __init__(self, model, view):
        ''' Connect presenter to model and view '''
        self.model = model
        self.view = view
        self.view.set_presenter(self)

    def build_tree(self, node):
        ''' Retrieve database metadata from Snowflake and build tree below node '''

        # Get node level
        if node.key == '':
            node_level = 'Root'
        else:
            node_level = node.values[0]

        tree_data = self.view.get_tree_data()
        if node_level == 'Root':
            scope = 'ACCOUNT'
            self.model.get_databases(tree_data, scope)
            self.model.get_schemas(tree_data, scope)
            for object_type in self.model.object_types:
                self.model.get_schema_objects(tree_data, object_type, scope)
        elif node_level == 'Database':
            scope = f'{node_level} {node.key}'
            self.model.get_schemas(tree_data, scope)
            for object_type in self.model.object_types:
                self.model.get_schema_objects(tree_data, object_type, scope)
        elif node_level == 'Schema':
            scope = f'{node_level} {node.key}'
            for object_type in self.model.object_types:
                self.model.get_schema_objects(tree_data, object_type, scope)
        elif node_level in self.model.object_types:
            scope = f'Schema {node.parent}'
            self.model.get_schema_objects(tree_data, node_level, scope)

        self.view.set_tree_data(tree_data)
        self.view.set_status_bar('Ready')

    def submit_query(self, query):
        ''' Submit query and return output '''

        if query:
            # Clear output values
            self.view.set_output_values(
                {
                    "-OUTPUT-": "",
                    "-QUERYID-": "",
                    "-QUERYDURATION-" : ""
                },
                False
            )

            # Execute query and return output
            output, query_details = self.model.run_query(query)

            # Display query output
            self.view.set_output_values(
                {
                    "-OUTPUT-": output,
                    "-QUERYID-": query_details['query_id'],
                    "-QUERYDURATION-" : query_details['query_duration']
                },
                query_details['query_error']
            )
        else:
            self.show_help(self.run_event)
