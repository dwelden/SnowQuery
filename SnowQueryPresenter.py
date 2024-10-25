class Presenter:
    def __init__(self, model, view):
        ''' Connect presenter to model and view '''
        self.model = model
        self.view = view
        self.view.presenter = self

    def build_tree(self, window, tree_data, node):
        ''' Retrieve database metadata from Snowflake and build tree below node '''

        # Get node level
        if node.key == '':
            node_level = 'Root'
        else:
            node_level = node.values[0]

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

        window['-TREE-'].update(values=tree_data)
        window['-STATUSBAR-'].update(value='Ready')

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

    def submit_query(self, query):
        ''' Execute query and display output '''
        output, query_details = self.model.run_query(query)
        return output, query_details
