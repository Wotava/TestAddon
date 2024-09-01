import bpy


class VIEW3D_PT_NodeTestPanel(bpy.types.Panel):
    bl_label = "Test Scene"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TEST'

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.operator("nodes.test_check", text="Test Scene Nodes")

