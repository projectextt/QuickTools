bl_info = {
    "name": "Quick Tools",
    "author": "projectextt",
    "version": (4, 0, 12),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > QuickTools",
    "description": "Kumpulan tools animasi dalam satu tab",
    "category": "Animation",
}
	
import bpy
import importlib
from bpy.app.handlers import persistent

# --- IMPORT ---
from . import addon_updater_ops

from .utils import  (
        license_check,
        )

from .core import   (
        library_logic,
        manager_logic,
        quick_pose_core,
        extra_logic,
        collection_logic,
        child_logic,
        quick_anim_layer,
        snap_logic,
        motion_path_logic,
        quick_display_layer,
        empty_logic,
        path_logic,
        )

# ui
from .ui import main_panel

# core.insert
from .core.insert import child_preset_logic


@persistent
def reload_preview_on_load(dummy):
    img = bpy.data.images.get("SLB_INTERNAL_PREVIEW")
    if img:
        img.use_fake_user = True
        
    timer_func = manager_logic.slb_preview_timer
    if not bpy.app.timers.is_registered(timer_func):
        bpy.app.timers.register(timer_func)

class QT_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    
    license_key: bpy.props.StringProperty(
        name="License Key",
        description="Masukkan License Key dari Admin",
        default="",
        subtype='PASSWORD'
    )

    # --- PROPERTI TAMBAHAN UNTUK UPDATER ---
    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for updates",
        description="If enabled, auto-check for updates using an interval",
        default=False,
    )
    updater_interval_months: bpy.props.IntProperty(name='Bulan', default=0)
    updater_interval_days: bpy.props.IntProperty(name='Hari', default=1)
    updater_interval_hours: bpy.props.IntProperty(name='Jam', default=0)
    updater_interval_minutes: bpy.props.IntProperty(name='Menit', default=0)

    def draw(self, context):
        layout = self.layout
        
        try:
            license_check.draw_preferences_license(self, context)
        except Exception as e:
            layout.label(text=f"License UI Error: {e}", icon='ERROR')

        layout.separator()

        
        # 2. Gambar Sistem Update (Hanya muncul jika lisensi aktif)
        if license_check.check_license(context):
            box = layout.box()
            # Panggil UI bawaan addon_updater
            addon_updater_ops.update_settings_ui(self, context)
        else:
            layout.label(text="Aktifkan lisensi untuk fitur update otomatis.", icon='INFO')


def register():
    # Register Updater
    addon_updater_ops.register(bl_info)
    
    bpy.utils.register_class(QT_Preferences)
    
    if reload_preview_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(reload_preview_on_load)
    
    timer_func = manager_logic.slb_preview_timer
    if not bpy.app.timers.is_registered(timer_func):
        bpy.app.timers.register(timer_func)
    
    license_check.register()
    library_logic.register()
    manager_logic.register()
    quick_pose_core.register()
    collection_logic.register()
    extra_logic.register()
    child_logic.register()
    child_preset_logic.register()
    motion_path_logic.register()
    quick_display_layer.register()
    quick_anim_layer.register()
    snap_logic.register()
    empty_logic.register()
    path_logic.register()
    main_panel.register()
    
def unregister():
    # Unregister Updater
    addon_updater_ops.unregister()
    
    timer_func = manager_logic.slb_preview_timer
    if bpy.app.timers.is_registered(timer_func):
        bpy.app.timers.unregister(timer_func)

    if reload_preview_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(reload_preview_on_load)
    
    main_panel.unregister()
    path_logic.unregister()
    empty_logic.unregister()
    snap_logic.unregister()
    quick_anim_layer.unregister()
    quick_display_layer.unregister()
    motion_path_logic.unregister()
    child_preset_logic.unregister()
    child_logic.unregister()
    extra_logic.unregister()
    collection_logic.unregister()
    quick_pose_core.unregister()
    manager_logic.unregister()
    library_logic.unregister()
    license_check.unregister()
    
    bpy.utils.unregister_class(QT_Preferences)
