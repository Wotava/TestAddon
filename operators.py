import bpy

max_frame_width = 1000
frame_internal_offset = 100


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

    def add_attribute(self, node) -> []:
        nodes = [node]
        tree = node.id_data
        if not tree:
            raise Exception

        for n_input in node.inputs:
            if len(n_input.links) > 0 or n_input.is_unavailable:
                continue

            attrib_node = tree.nodes.new('ShaderNodeAttribute')
            attrib_node.location = node.location
            attrib_node.location.x -= node.width / 2
            attrib_node.location.x -= attrib_node.width / 2
            attrib_node.location.y -= 45 * len(nodes)

            attrib_node.attribute_name = n_input.name

            if n_input.type == 'VECTOR':
                n_output = attrib_node.outputs['Vector']
            elif n_input == 'VALUE':
                n_output = attrib_node.outputs['Fac']
            else:
                n_output = attrib_node.outputs['Color']
            tree.links.new(n_output, n_input)
            attrib_node.hide = True

            nodes.append(attrib_node)

        return nodes

    def get_bbox(self, nodes: list):
        bbox_min, bbox_max = None, None

        for node in nodes:
            lt_corner = node.location.copy()
            lt_corner.x -= node.width / 2
            lt_corner.y += node.height / 2

            rb_corner = node.location.copy()
            rb_corner.x += node.width / 2
            rb_corner.y -= node.height / 2

            if not bbox_max:
                bbox_max = lt_corner
                bbox_min = rb_corner
            else:
                bbox_min.x = min(bbox_min.x, rb_corner.x)
                bbox_min.y = min(bbox_min.y, rb_corner.y)
                bbox_max.x = max(bbox_max.x, lt_corner.x)
                bbox_max.x = max(bbox_max.y, lt_corner.y)

        height = abs(bbox_max.y - bbox_min.y)
        width = abs(bbox_max.x - bbox_min.x)
        center = (bbox_max + bbox_min) / 2
        return width, height, center

    def execute(self, context):
        disconnected_groups = []
        all_disconnected_nodes = []

        for mat in bpy.data.materials:
            if not mat.use_nodes or mat.node_tree is None:
                continue

            mat_root = self.find_root(mat.node_tree, 'OUTPUT_MATERIAL')
            if not mat_root:
                print(f"{mat.name}: No active material output")
                continue

            connected_nodes = self.parse_linked_input_nodes(mat_root)
            connected_width, connected_height, connected_location = self.get_bbox(connected_nodes)

            all_nodes = set(self.get_all_nodetree_nodes(mat.node_tree, extend_groups=False))
            disconnected_nodes = all_nodes.difference(set(connected_nodes))

            if len(disconnected_nodes) > 0:
                row_max_height = -1
                row_count = 0
                row_height_offset = 0
                row_width = max_frame_width

                frame_node = mat.node_tree.nodes.new('NodeFrame')
                frame_node.location = connected_location.copy()
                frame_node.location.y += connected_height

                for node in disconnected_nodes:
                    if node.type == 'FRAME':
                        continue

                    group = self.add_attribute(node)
                    group_width, group_height, group_location = self.get_bbox(group)
                    row_max_height = max(row_max_height, group_height)

                    if group_width > row_width:
                        row_count += 1
                        row_width = max_frame_width
                        row_height_offset += row_max_height
                        row_max_height = -1

                    loc = connected_location.copy()
                    loc.y += connected_height + row_height_offset + group_height / 2
                    loc.x += (max_frame_width - row_width) + group_width / 2
                    offset = loc - group_location

                    for sub_node in group:
                        sub_node.location += offset
                        sub_node.parent = frame_node

                    row_width -= group_width

                    print(f"\"{mat.name}\": {node.name} (type: {node.type})")
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