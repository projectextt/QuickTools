import bpy
from . import updater_core

class QT_OT_CheckUpdate(bpy.types.Operator):
    bl_idname = "quicktools.check_update"
    bl_label = "Check for Update"
    bl_description = "Cek apakah ada versi baru di GitHub"

    def execute(self, context):
        updater_core.check_for_update()
        return {'FINISHED'}

class QT_OT_DoUpdate(bpy.types.Operator):
    bl_idname = "quicktools.do_update"
    bl_label = "Install Update Now"
    bl_description = "Download dan install update (Blender akan otomatis tertutup)"

    def execute(self, context):
        updater_core.run_update_process()
        return {'FINISHED'}

class QT_OT_UpdateSuccessReport(bpy.types.Operator):
    bl_idname = "quicktools.update_success_report"
    bl_label = "Installation Report"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        # Tombol OK yang akan menutup Blender secara resmi
        bpy.ops.wm.quit_blender()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="QuickTools berhasil di-update!", icon='FILE_TICK')
        col.label(text="Klik OK untuk menutup Blender")
        col.label(text="Pastikan kerjaan udah disave")

def updater_draw_preferences(parent, context):
    layout = parent.layout
    col = layout.column(align=True)
    col.separator()
    col.label(text="QuickTools Updater", icon='FILE_REFRESH')
    
    col.separator()
    col.separator()
    
    # Tombol Check
    col.operator("quicktools.check_update", icon='WORLD')
    
    # Munculkan tombol install jika ada update
    if updater_core.update_available:
        col.alert = True
        col.operator("quicktools.do_update", text=f"Install Update v{updater_core.latest_version}")

def register():
    bpy.utils.register_class(QT_OT_CheckUpdate)
    bpy.utils.register_class(QT_OT_DoUpdate)
    bpy.utils.register_class(QT_OT_UpdateSuccessReport)

def unregister():
    bpy.utils.unregister_class(QT_OT_UpdateSuccessReport)
    bpy.utils.unregister_class(QT_OT_DoUpdate)
    bpy.utils.unregister_class(QT_OT_RestartBlender)