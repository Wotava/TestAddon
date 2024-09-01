if "bpy" in locals():
    import importlib

else:
    import bpy

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

]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    # Unregister this addon
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)