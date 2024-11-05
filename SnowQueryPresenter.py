class Presenter:
    def __init__(self, model, view):
        ''' Connect presenter to model and view '''
        self.model = model
        self.view = view
        self.view.set_presenter(self)

    def build_tree(self, tree_data, node_level, scope):
        ''' Retrieve database metadata from Snowflake and build tree below node '''

        schema_object_list = self.model.get_schema_object_list(node_level, scope)

        for schema_object in schema_object_list:
            parent = schema_object["parent"]
            name = schema_object["name"]
            formatted_name = schema_object["formatted_name"]
            object_type = schema_object["object_type"]
            if object_type == "object_header":
                level = name
            elif object_type in self.model.object_types:
                level = "leaf"
            else:
                level = object_type
            tree_data.Insert(parent, formatted_name, name, [level,])

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
