import bpy
import mathutils
from bpy.types import Menu

bl_info = {
    "name": "Origin2Selection",
    "description": "Move Object Origin to selected part of the mesh.",
    "version": (1, 0),
    "blender": (4, 0, 2),
    "category": "Mesh",
}

def midpoint(vertices):
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

        if len(mesh.vertices) == 1:
            obj.location = mesh.vertices.active.co
        elif len(mesh.edges) == 1:
            edge = mesh.edges.active
            obj.location = midpoint([mesh.vertices[index] for index in edge.vertices])
        elif len(mesh.polygons) == 1:
            face = mesh.polygons.active
            obj.location = midpoint([mesh.vertices[index] for index in face.vertices])
        else:
            selected_verts = [v for v in mesh.vertices if v.select]
            if len(selected_verts) == 1:
                obj.location = selected_verts[0].co
            else:
                obj.location = midpoint([v.co for v in selected_verts])

        return {'FINISHED'}

def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(OriginToSelectionOperator.bl_idname, text="Origin to Selection")

classes = (
    OriginToSelectionOperator,
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_snap.append(menu_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Mesh', space_type='VIEW_3D')
        kmi = km.keymap_items.new(OriginToSelectionOperator.bl_idname, type='O', value='PRESS', shift=False, ctrl=True, alt=False)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.types.VIEW3D_MT_snap.remove(menu_func)
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
