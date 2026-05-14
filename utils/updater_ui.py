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
    
    # 1. Gunakan Box agar terpisah secara visual
    main_box = layout.box()
    
    # Header dengan Icon
    header = main_box.row()
    header.label(text="QUICKTOOLS AUTO-UPDATER", icon='SETTINGS')
    
    # Baris Info Versi
    row_ver = main_box.row(align=True)
    current_ver_str = ".".join(map(str, updater_core.CURRENT_VERSION))
    
    # Gunakan split agar label dan info sejajar rapi
    split = row_ver.split(factor=0.4)
    split.label(text="Installed Version:", icon='FILE_TICK')
    split.label(text=current_ver_str)
    
    main_box.separator()

    # 2. Area Aksi (Tombol)
    col = main_box.column(align=True)
    
    if not updater_core.update_available:
        # Tampilan jika sudah versi terbaru (Lebih kalem)
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator("quicktools.check_update", text="Check for Updates", icon='WORLD')
        
        # Info tambahan kecil di bawahnya
        col.label(text="Versi yg lu pasang udeh paling baru.", icon='CHECKMARK')
        
    else:
        # Tampilan jika ADA update (Lebih mencolok/Alert)
        box_update = col.box()
        sub_col = box_update.column(align=True)
        
        # Info versi baru
        row_new = sub_col.row()
        row_new.alert = True
        row_new.label(text=f"Versi Baru Tersedia: v{updater_core.latest_version}", icon='info')
        
        sub_col.separator()
        
        # Tombol Update yang besar dan jelas
        row_btn = sub_col.row()
        row_btn.scale_y = 1.5
        row_btn.operator("quicktools.do_update", text=f"Install Update v{updater_core.latest_version}")

def register():
    bpy.utils.register_class(QT_OT_CheckUpdate)
    bpy.utils.register_class(QT_OT_DoUpdate)
    bpy.utils.register_class(QT_OT_UpdateSuccessReport)

def unregister():
    bpy.utils.unregister_class(QT_OT_UpdateSuccessReport)
    bpy.utils.unregister_class(QT_OT_DoUpdate)
    bpy.utils.unregister_class(QT_OT_RestartBlender)