bl_info = {
    "name": "Origin Snap",
    "category": "Mesh",
    "author": "Jakub Jaszewski",
    "description": "Manipulate Object Origin position.",
    "version": (2, 1),
    "blender": (4, 2, 0),
    "tracker_url": "https://github.com/j-jasz/origin_snap/issues",
}

import bpy
import bmesh
import mathutils
from bpy import context
from bpy.types import Menu, Operator

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

        origin_offset = obj.location
        vertices = [v.co for v in bpy.context.active_object.data.vertices]

        for vertex in mesh.vertices:
            vertex.co += origin_offset
        obj.location = (0, 0, 0)

        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

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
        bm = bmesh.from_edit_mesh(mesh)

        vertices = [v.co for v in bm.verts if v.select]
        if len(vertices) == 0:
            self.report({'ERROR'}, "No vertices selected.")
            return {'CANCELLED'}

        midpoint = mathutils.Vector()
        midpoint += sum(vertices, mathutils.Vector()) / len(vertices)

        for v in bm.verts:
            v.co -= midpoint
        obj.location += midpoint

        bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}

#====================================================

class VIEW_MT_PIE_OriginSnap(bpy.types.Menu):
    bl_label = "Origin / Object Snap"
    bl_idname = "VIEW_MT_PIE_origin_snap"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        pie.operator("object.move_to_world_origin", text="Object to World Origin")
        pie.operator("mesh.origin_to_selection", text="Origin to Selection")
        pie.operator("mesh.origin_to_world_origin", text="Origin to World Origin")
        op = pie.operator("object.origin_set", text="Origin to Geometry")
        op.type = 'ORIGIN_GEOMETRY'
        op = pie.operator("object.origin_set", text="Geometry to Origin")
        op.type = 'GEOMETRY_ORIGIN'

#====================================================

def menu_func(self, context):
    layout = self.layout
    layout.operator(ObjectToWorldOriginOperator.bl_idname, text="Object to World Origin")
    layout.operator(OriginToSelectionOperator.bl_idname, text="Origin to Selection")
    layout.operator(OriginToWorldOriginOperator.bl_idname, text="Origin to World Origin")
    layout.operator("object.origin_set", text="Origin to Geometry").type = 'ORIGIN_GEOMETRY'
    layout.operator("object.origin_set", text="Geometry to Origin").type = 'GEOMETRY_ORIGIN'

classes = (
    ObjectToWorldOriginOperator,
    OriginToSelectionOperator,
    OriginToWorldOriginOperator,
)

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_snap.append(menu_func)
    bpy.utils.register_class(VIEW_MT_PIE_OriginSnap)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu_pie", 'W', 'PRESS', ctrl=True)
        kmi.properties.name = "VIEW_MT_PIE_origin_snap"
        addon_keymaps.append((km, kmi))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_snap.remove(menu_func)
    bpy.utils.unregister_class(VIEW_MT_PIE_OriginSnap)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        for km, kmi in list(addon_keymaps):
            try:
                km.keymap_items.remove(kmi)
            except ValueError:
                print(f"Warning: Keymap item {kmi} not found in keymap {km.name}.  It may have already been removed.")
            addon_keymaps.remove((km, kmi))

if __name__ == "__main__":
    register()
