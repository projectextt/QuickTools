import bpy
from . import updater_core

class QT_OT_CheckUpdate(bpy.types.Operator):
    bl_idname = "quicktools.check_update"
    bl_label = "Check for Update"
    bl_description = "Cek apakah ada versi baru"

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

# --- OPERATOR RESTORE ---
class QT_OT_RestoreBackup(bpy.types.Operator):
    bl_idname = "quicktools.restore_backup"
    bl_label = "Kembalikan Versi Sebelumnya"
    bl_description = "Mengembalikan QuickTools ke versi sebelum update terakhir"

    def execute(self, context):
        updater_core.run_restore_process()
        return {'FINISHED'}

def updater_draw_preferences(parent, context):
    layout = parent.layout
    core = updater_core # Alias biar pendek manggilnya
    
    main_box = layout.box()
    
    # 1. HEADER & INFO VERSI (Tetap ada di semua kondisi)
    row_info = main_box.row()
    row_info.label(text="QUICKTOOLS UPDATER", icon='SETTINGS')
    
    curr_v = ".".join(map(str, core.CURRENT_VERSION))
    row_info.label(text=f"Versi: {curr_v}")

    main_box.separator()

    # 2. STATE-BASED UI (Logika Kondisional)
    
    # --- KONDISI: LATEST (Sudah Terbaru) ---
    if core.status == 'LATEST':
        row = main_box.row(align=True)
        # Sisi Kiri: Label status
        row.label(text="Versi lu udeh paling baru.", icon='CHECKMARK')
        # Sisi Kanan: Tombol Refresh kecil (Style side-by-side)
        row.operator("quicktools.check_update", text="", icon='FILE_REFRESH')

    # --- KONDISI: CHECKING (Lagi Loading) ---
    elif core.status == 'CHECKING':
        row = main_box.row()
        row.enabled = False # Matikan tombol biar gak di-spam
        row.operator("quicktools.check_update", text="Menghubungi GitHub...", icon='WORLD')

    # --- KONDISI: UPDATE_READY (Ada Barang Baru) ---
    elif core.status == 'UPDATE_READY' or core.update_available:
        row_action = main_box.row(align=False)
        row_action.scale_y = 1.3
        
        # Tombol Update (Kiri)
        col_up = row_action.column(align=True)
        col_up.alert = True
        col_up.operator("quicktools.do_update", text=f"Instal v{core.latest_version}", icon='IMPORT')
        
        # Tombol Restore (Kanan - Jika ada backup)
        if core.check_backup_exists():
            col_res = row_action.column(align=True)
            col_res.operator("quicktools.restore_backup", text="Kembalikan Versi", icon='LOOP_BACK')

    # --- KONDISI: IDLE / ERROR (Kondisi Awal atau Gagal) ---
    else:
        col = main_box.column(align=True)
        if core.status == 'ERROR':
            col.label(text=core.error_message, icon='ERROR')
        
        col.scale_y = 1.2
        col.operator("quicktools.check_update", text="Periksa Pembaruan Sekarang", icon='WORLD')

    # 3. FOOTER (Informasi Terakhir Dicek)
    main_box.separator()
    main_box.label(text=f"Terakhir diperiksa: {core.last_check}", icon='TIME')

def register():
    bpy.utils.register_class(QT_OT_CheckUpdate)
    bpy.utils.register_class(QT_OT_DoUpdate)
    bpy.utils.register_class(QT_OT_UpdateSuccessReport)
    bpy.utils.register_class(QT_OT_RestoreBackup)

def unregister():
    bpy.utils.unregister_class(QT_OT_RestoreBackup)
    bpy.utils.unregister_class(QT_OT_UpdateSuccessReport)
    bpy.utils.unregister_class(QT_OT_DoUpdate)
    bpy.utils.unregister_class(QT_OT_RestartBlender)