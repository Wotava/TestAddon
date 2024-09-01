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

    def add_attribute(self, node):
        tree = node.id_data
        counter = 0
        for n_input in node.inputs:
            if len(n_input.links) > 0:
                continue

            attrib_node = tree.nodes.new('ShaderNodeAttribute')
            attrib_node.location = node.location
            attrib_node.location.x -= node.width / 2
            attrib_node.location.x -= attrib_node.width / 2
            attrib_node.location.y -= 45 * counter
            counter += 1

            attrib_node.attribute_name = n_input.name

            if n_input.type == 'VECTOR':
                n_output = attrib_node.outputs['Vector']
            elif n_input == 'VALUE':
                n_output = attrib_node.outputs['Fac']
            else:
                n_output = attrib_node.outputs['Color']
            tree.links.new(n_output, n_input)
            attrib_node.hide = True

    def get_bbox(self, nodes: list):
        bbox_min, bbox_max = None, None

        for node in nodes:
            lt_corner = node.location.copy()
            lt_corner.x -= node.width / 2
            lt_corner.y -= node.height / 2

            rt_corner = node.location.copy()
            rt_corner.x += node.width / 2
            rt_corner.y += node.height / 2

            if not bbox_max:
                bbox_max = lt_corner
                bbox_min = rt_corner
            else:
                bbox_max = max(bbox_max, lt_corner)
                bbox_min = max(bbox_min, rt_corner)

        height = abs(bbox_max.y - bbox_min.y)
        width = abs(bbox_max.x - bbox_min.x)
        center = (bbox_max + bbox_min) / 2
        return width, height, center

    def execute(self, context):
        disconnected_groups = []
        all_disconnected_nodes = []

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
                print(f"\nMaterial \"{mat.name}\" disconnected nodes: ")
                for node in disconnected_nodes:
                    print(f"->{node.name} (type: {node.type})")

                    self.add_attribute(node)

                    if node.type == 'GROUP' and node.node_tree not in disconnected_groups:
                        disconnected_groups.append(node.node_tree)
                all_disconnected_nodes.extend(disconnected_nodes)

        if len(all_disconnected_nodes) == 0:
            print(f"No disconnected shader nodes")

        for group in disconnected_groups:
            print(f"\nDisconnected group {group.name} used in: ")
            for mat in bpy.data.materials:
                if not mat.use_nodes:
                    continue
                if self.find_group_usages(group, mat.node_tree):
                    print(f"->{mat.name}")

        if len(disconnected_groups) == 0:
            print(f"No disconnected Node Groups")

        broken_groups = []
        for group in bpy.data.node_groups:
            if group.type == 'SHADER':
                if group.users == 0:
                    print(f"{group.name} is unused")
                    continue

                root = self.find_root(group, 'GROUP_OUTPUT')
                if not root:
                    print(f"{group.name} has no valid output node")
                    continue

                connected_nodes = set(self.parse_linked_input_nodes(root))
                all_nodes = set(self.get_all_nodetree_nodes(group, extend_groups=False))
                delta = all_nodes.difference(connected_nodes)

                if len(delta) == 0:
                    continue

                print(f"\n{group.name} has unused nodes: ")
                for node in delta:
                    print(f"->{node.name} (type: {node.type})")

                broken_groups.append(group)

        if len(broken_groups) == 0:
            print(f"No disconnected shader nodes in Node Groups")

        return {'FINISHED'}