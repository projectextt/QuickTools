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
    core = updater_core
    
    # Bungkus dalam satu Box utama
    main_box = layout.box()
    
    # Header & Info Versi (Statis)
    header = main_box.row()
    header.label(text="PENGATURAN PEMBARUAN QUICKTOOLS", icon='SETTINGS')
    
    curr_v = ".".join(map(str, core.CURRENT_VERSION))
    header.label(text=f"Versi: {curr_v}")

    main_box.separator()

    # --- BARIS AKSI UTAMA (Side-by-Side) ---
    # Kita bagi dua kolom: Kiri (Status/Update), Kanan (Restore)
    row_action = main_box.row(align=False)
    row_action.scale_y = 1.3

    # === SISI KIRI: STATUS / UPDATE ===
    col_left = row_action.column(align=True)
    
    if core.status == 'CHECKING':
        col_left.enabled = False
        col_left.operator("quicktools.check_update", text="Menghubungi GitHub...", icon='WORLD')
    
    elif core.status == 'UPDATE_READY':
        col_left.alert = True
        col_left.operator("quicktools.do_update", text=f"Instal Update v{core.latest_version}", icon='IMPORT')
        
    else:
        # Kondisi LATEST atau IDLE
        sub_row = col_left.row(align=True)
        
        # Tombol Label (Mati jika sudah terbaru)
        btn_label = "Versi lu udeh paling baru." if core.status == 'LATEST' else "Periksa Pembaruan Sekarang"
        label_op = sub_row.operator("quicktools.check_update", text=btn_label)
        if core.status == 'LATEST':
            sub_row.enabled = False # Tombol kiri jadi abu-abu
            
        # Tombol Refresh Kecil (Selalu Aktif di sebelah kanan label)
        refresh_row = sub_col_refresh = sub_row.column(align=True) # Trick buat dapet kolom baru dlm row
        refresh_row.enabled = True 
        refresh_row.operator("quicktools.check_update", text="", icon='FILE_REFRESH')

    # === SISI KANAN: MAINTENANCE / RESTORE ===
    col_right = row_action.column(align=True)
    
    # Cek folder backup dengan Try-Except (Self-Report)
    backup_ready = False
    try:
        backup_ready = core.check_backup_exists()
    except Exception as e:
        print(f"QuickTools Error: Gagal akses folder backup - {e}")
        # Tetap False jika error

    # Tombol Restore (Selalu ada, tapi Disable kalau gak ada backup)
    row_res = col_right.row()
    row_res.enabled = backup_ready
    row_res.operator("quicktools.restore_backup", text="Kembalikan Versi", icon='LOOP_BACK')

    # --- FOOTER INFO ---
    main_box.separator()
    footer = main_box.row()
    footer.scale_y = 0.8
    
    if core.status == 'ERROR':
        footer.label(text=core.error_message, icon='ERROR')
    else:
        footer.label(text=f"Terakhir diperiksa: {core.last_check}", icon='TIME')

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