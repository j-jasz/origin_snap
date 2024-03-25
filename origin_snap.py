import bpy
import mathutils
from bpy.types import Menu

bl_info = {
    "name": "OriginSnap",
    "description": "Manipulate Object Origin position.",
    "version": (1, 0),
    "blender": (4, 0, 2),
    "category": "Mesh",
}

# Reusable function for calculating midpoint
def midpoint(vertices):
    if not vertices:
        return None
    return sum(vertices, mathutils.Vector()) / len(vertices)

class OriginToSelectionOperator(bpy.types.Operator):
    bl_idname = "mesh.origin_to_selection"
    bl_label = "Origin to Selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == 'EDIT_MESH'

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        if context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Please switch to Edit Mode.")
            return {'CANCELLED'}

        if len(mesh.vertices) == 0:
            self.report({'ERROR'}, "No vertices selected.")
            return {'CANCELLED'}

        # Store active mode
        mode = bpy.context.active_object.mode

        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get selected vertices' coordinates
        vertices = [v.co for v in bpy.context.active_object.data.vertices if v.select]

        # Calculate the midpoint
        v_mid_point = midpoint(vertices)

        # Move object origin to midpoint
        obj.location += v_mid_point

        # Adjust the mesh data vertices to maintain their positions relative to the new origin
        for vertex in mesh.vertices:
            vertex.co -= v_mid_point

        # Switch back to previous mode
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

class OriginToWorldOriginOperator(bpy.types.Operator):
    bl_idname = "mesh.origin_to_world_origin"
    bl_label = "Origin to World Origin"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        mode = bpy.context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get object origin location
        origin_offset = obj.location

        # Get selected vertices' coordinates
        vertices = [v.co for v in bpy.context.active_object.data.vertices]

        # Adjust the mesh data vertices position by location offset
        for vertex in mesh.vertices:
            vertex.co += origin_offset

        # Move object origin to world origin
        obj.location = (0, 0, 0)

        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

class ObjectToWorldOriginOperator(bpy.types.Operator):
    bl_idname = "object.move_to_world_origin"
    bl_label = "Object to World Origin"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        obj.location = (0, 0, 0)
        return {'FINISHED'}

def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(OriginToSelectionOperator.bl_idname, text="Origin to Selection")
    layout.operator(OriginToWorldOriginOperator.bl_idname, text="Origin to World Origin")
    layout.operator(ObjectToWorldOriginOperator.bl_idname, text="Object to World Origin")

classes = (
    OriginToSelectionOperator,
    OriginToWorldOriginOperator,
    ObjectToWorldOriginOperator,
)

# ~ addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_snap.append(menu_func)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_snap.remove(menu_func)

# ~ def register():
    # ~ for cls in classes:
        # ~ bpy.utils.register_class(cls)
    # ~ bpy.types.VIEW3D_MT_snap.append(menu_func)

    # ~ wm = bpy.context.window_manager
    # ~ kc = wm.keyconfigs.addon
    # ~ if kc:
        # ~ km = kc.keymaps.new(name='Mesh', space_type='VIEW_3D')
        # ~ kmi = km.keymap_items.new(OriginToSelectionOperator.bl_idname, type='O', value='PRESS', shift=False, ctrl=True, alt=False)
        # ~ addon_keymaps.append((km, kmi))

# ~ def unregister():
    # ~ bpy.types.VIEW3D_MT_snap.remove(menu_func)
    # ~ for cls in classes:
        # ~ bpy.utils.unregister_class(cls)

    # ~ wm = bpy.context.window_manager
    # ~ kc = wm.keyconfigs.addon
    # ~ if kc:
        # ~ for km, kmi in addon_keymaps:
            # ~ km.keymap_items.remove(kmi)
    # ~ addon_keymaps.clear()

if __name__ == "__main__":
    register()
