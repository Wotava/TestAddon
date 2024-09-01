if "bpy" in locals():
    import importlib
    importlib.reload(operators)
    importlib.reload(ui)
else:
    import bpy
    from . import operators
    from . import ui

bl_info = {
    'name': 'Test',
    'description': 'Whatever',
    'location': '3D View -> Toolbox',
    'author': 'wotava',
    'version': (1, 0),
    'blender': (4, 0, 0),
    'category': 'Object'
}
classes = [
    operators.NODE_OP_CheckNodes,
    ui.VIEW3D_PT_NodeTestPanel
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    # Unregister this addon
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)