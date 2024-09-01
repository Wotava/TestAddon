import bpy


class NODE_OP_CheckNodes(bpy.types.Operator):
    """"""
    bl_label = "Test Check"
    bl_idname = "nodes.test_check"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def find_root(self, node_tree, node_type):
        for node in node_tree.nodes:
            if node.type == node_type and node.is_active_output:
                return node
        return None

    def parse_linked_input_nodes(self, node) -> []:
        links = [node]
        for n_input in node.inputs:
            if len(n_input.links) > 0:
                links.extend(
                    [x for x in self.parse_linked_input_nodes(n_input.links[0].from_node) if x not in links])
        return links

    def find_group_usages(self, node_group, dest_tree) -> bool:
        for node in dest_tree.nodes:
            if node.type == 'GROUP':
                if node.node_tree.name == node_group.name:
                    return True
                else:
                    if self.find_group_usages(node_group, node.node_tree):
                        return True
        return False

    def get_all_nodetree_nodes(self, node_tree, extend_groups=True) -> []:
        nodes = list(node_tree.nodes)
        checked_node_groups = []

        if extend_groups:
            for node in nodes:
                if node.type == 'GROUP' and node.node_tree.name not in checked_node_groups:
                    nodes.extend(self.get_all_nodetree_nodes(node.node_tree))

        return nodes

    def execute(self, context):
        disconnected_groups = []

        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue

            mat_root = self.find_root(mat.node_tree, 'OUTPUT_MATERIAL')
            if not mat_root:
                print(f"{mat.name}: No active material output")
                continue

            connected_nodes = self.parse_linked_input_nodes(mat_root)
            all_nodes = set(self.get_all_nodetree_nodes(mat.node_tree, extend_groups=False))
            disconnected_nodes = all_nodes.difference(set(connected_nodes))
            if len(disconnected_nodes) > 0:
                print(f"\nMat {mat.name} disconnected nodes: ")
                for node in disconnected_nodes:
                    print(f"{node.name} (type: {node.type})")
                    if node.type == 'GROUP' and node.node_tree not in disconnected_groups:
                        disconnected_groups.append(node.node_tree)


        for group in disconnected_groups:
            print(f"\nDisconnected group {group.name} used in: ")
            for mat in bpy.data.materials:
                if not mat.use_nodes:
                    continue
                if self.find_group_usages(group, mat.node_tree):
                    print(mat.name)

        for group in bpy.data.node_groups:
            if group.type == 'SHADER':
                root = self.find_root(group, 'GROUP_OUTPUT')
                if not root:
                    continue
                connected_nodes = set(self.parse_linked_input_nodes(root))
                all_nodes = set(self.get_all_nodetree_nodes(group, extend_groups=False))
                delta = all_nodes.difference(connected_nodes)

                if len(delta) == 0:
                    continue

                print(f"\n{group.name} unused nodes: ")
                for node in delta:
                    print(f"{node.name} (type: {node.type})")

        return {'FINISHED'}