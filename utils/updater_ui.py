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
    
    # Ambil data tanggal dari Preferences (Bukan dari variabel sementara)
    addon_name = __package__.split('.')[0]
    prefs = context.preferences.addons[addon_name].preferences
    
    main_box = layout.box()
    
    # 1. HEADER (Info Versi)
    header = main_box.row()
    header.label(text="PENGATURAN PEMBARUAN QUICKTOOLS", icon='SETTINGS')
    curr_v = ".".join(map(str, core.CURRENT_VERSION))
    header.label(text=f"Versi: {curr_v}")

    main_box.separator()

    # 2. AREA AKSI (Side-by-Side Statis)
    row_action = main_box.row(align=True) # align=True biar nempel rapi tapi punya sekat
    row_action.scale_y = 1.3

    # --- SISI KIRI: TOMBOL UTAMA (CEK / INSTAL) ---
    col_main = row_action.column(align=True)
    
    if core.status == 'CHECKING':
        col_main.enabled = False
        col_main.operator("quicktools.check_update", text="Menghubungi GitHub...", icon='WORLD')
    elif core.status == 'UPDATE_READY':
        col_main.alert = True # Warna Merah
        col_main.operator("quicktools.do_update", text=f"Instal v{core.latest_version}", icon='IMPORT')
    else:
        # Kondisi LATEST atau IDLE
        col_main.enabled = (core.status != 'LATEST') # Mati cuma kalau statusnya LATEST
        btn_text = "Versi lu udeh paling baru." if core.status == 'LATEST' else "Periksa Pembaruan"
        col_main.operator("quicktools.check_update", text=btn_text)

    # --- SISI KANAN: TOMBOL REFRESH (SELALU ADA & NYALA) ---
    col_refresh = row_action.column(align=True)
    col_refresh.scale_x = 1.2 # Biar kotaknya agak proporsional buat ikon
    col_refresh.operator("quicktools.check_update", text="", icon='FILE_REFRESH')

    # === SISI JAUH KANAN: RESTORE ===
    row_action.separator()
    col_res = row_action.column(align=True)

    # Kita taruh pengecekannya di sini sebelum menggambar tombol
    backup_ready = False
    try:
        backup_ready = core.check_backup_exists()
    except Exception as e:
        # Self-report ke console kalau ada masalah sistem
        print(f"QuickTools UI Error: Gagal deteksi backup - {e}")

    # Tombol Restore (Selalu ada, tapi Disable/Abu-abu kalau gak ada backup)
    col_res.enabled = backup_ready 
    col_res.operator("quicktools.restore_backup", text="Kembalikan Versi", icon='LOOP_BACK')

    # 3. FOOTER (Info Waktu dari Preferences)
    main_box.separator()
    if core.status == 'ERROR':
        main_box.label(text=core.error_message, icon='ERROR')
    else:
        # Baca dari prefs.last_update_check, bukan dari core.last_check
        main_box.label(text=f"Terakhir diperiksa: {prefs.last_update_check}", icon='TIME')

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