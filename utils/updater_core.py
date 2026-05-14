import bpy, os, shutil, urllib.request, zipfile, json
import addon_utils
from datetime import datetime

# --- CONFIG ---
GITHUB_USER = "projectextt"
GITHUB_REPO = "QuickTools"
TOKEN = "" # Kosongkan jika Public. Isi "ghp_xxx" jika Private.


# --- PATHS ---
doc_path = os.path.join(os.path.expanduser("~"), "Documents", "QuickTools", "Blender 4.2", "__updater__")
backup_path = os.path.join(doc_path, "__backup__")
source_path = os.path.join(doc_path, "__source__")


# --- STATE MANAGEMENT ---
# Status: 'IDLE', 'CHECKING', 'UPDATE_READY', 'LATEST', 'ERROR'
status = 'IDLE'
last_check = "Belum pernah diperiksa"
update_available = False
latest_version = ""
download_url = ""
error_message = ""

# Ambil versi dari metadata addon secara otomatis
def get_current_version():
    """Mengambil versi langsung dari bl_info addon ini secara akurat"""
    addon_name = __package__.split('.')[0]
    for mod in addon_utils.modules():
        if mod.__name__ == addon_name:
            # Mengambil tuple version, misal (4, 0, 1)
            return mod.bl_info.get('version', (0, 0, 0))
    return (0, 0, 0)

CURRENT_VERSION = get_current_version()

def show_message(message="", title="QuickTools Update", icon='INFO'):
    def draw(self, context): self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def check_for_update():
    global status, update_available, latest_version, download_url, last_check, error_message
    
    # RAWAN 1: Koneksi internet & Parsing JSON
    try:
        status = 'CHECKING'
        # Update waktu pemeriksaan
        last_check = datetime.now().strftime("%d-%m-%Y %H:%M")
        
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url)
        if TOKEN: req.add_header('Authorization', f'token {TOKEN}')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            tag = data['tag_name'].replace('v', '').replace('update ', '')
            ver_tuple = tuple(map(int, tag.split('.')))
            
            if ver_tuple > CURRENT_VERSION:
                status = 'UPDATE_READY'
                update_available = True
                latest_version = tag
                download_url = data['zipball_url']
            else:
                status = 'LATEST'
                update_available = False
                
    except Exception as e:
        status = 'ERROR'
        error_message = f"Gagal cek update: {str(e)}"
        # Self-report ke console dan popup
        print(f"DEBUG: {error_message}")

def run_update_process():
    try:
        # 1. Siapkan Folder
        for p in [backup_path, source_path]:
            if os.path.exists(p): shutil.rmtree(p)
            os.makedirs(p)

        # 2. Backup Addon Sekarang
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        try:
            shutil.copytree(addon_dir, os.path.join(backup_path, "QuickTools_Backup"))
        except Exception as e:
            raise Exception(f"Gagal Backup: {e}")

        # 3. Download ZIP
        zip_file = os.path.join(source_path, "update.zip")
        try:
            req = urllib.request.Request(download_url)
            if TOKEN: req.add_header('Authorization', f'token {TOKEN}')
            with urllib.request.urlopen(req) as response, open(zip_file, 'wb') as f:
                f.write(response.read())
        except Exception as e:
            raise Exception(f"Gagal Download: {e}")

        # 4. Extract
        extract_to = os.path.join(source_path, "extracted")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        # 5. Cari Folder Utama di dalam ZIP
        subdirs = [d for d in os.listdir(extract_to) if os.path.isdir(os.path.join(extract_to, d))]
        if not subdirs: raise Exception("ZIP Struktur Salah")
        new_content_dir = os.path.join(extract_to, subdirs[0])

        # 6. Cleaning Agresif (Hapus .pyc lama dan __pycache__)
        for root, dirs, files in os.walk(addon_dir):
            for f in files:
                if f.endswith(".pyc") or f.endswith(".pyo"):
                    try: os.remove(os.path.join(root, f))
                    except: pass

        # 7. Timpa File Baru
        for item in os.listdir(new_content_dir):
            s = os.path.join(new_content_dir, item)
            d = os.path.join(addon_dir, item)
            if os.path.isdir(s):
                if os.path.exists(d): shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        # 8. Selesai
        bpy.ops.quicktools.update_success_report('INVOKE_DEFAULT')
        
    except Exception as e:
        show_message(str(e), title="Update Gagal", icon='ERROR')

def check_backup_exists():
    """Cek apakah folder backup ada isinya"""
    backup_addon_path = os.path.join(backup_path, "QuickTools_Backup")
    return os.path.exists(backup_addon_path)

def run_restore_process():
    """Proses mengembalikan addon ke versi sebelumnya"""
    try:
        backup_addon_path = os.path.join(backup_path, "QuickTools_Backup")
        addon_dir = os.path.dirname(os.path.dirname(__file__))

        # RAWAN 1: Cek folder backup
        if not os.path.exists(backup_addon_path):
            raise Exception("Folder backup tidak ditemukan!")

        # RAWAN 2: Hapus versi yang sekarang (Cleaning)
        # Kita hapus dulu folder yang sekarang biar gak numpuk
        if os.path.exists(addon_dir):
            shutil.rmtree(addon_dir)

        # RAWAN 3: Copy balik dari backup
        shutil.copytree(backup_addon_path, addon_dir)

        # Berhasil! Panggil dialog sukses
        bpy.ops.quicktools.update_success_report('INVOKE_DEFAULT')

    except Exception as e:
        show_message(f"Restore Gagal: {str(e)}", title="Error Restore", icon='ERROR')

def register():
    if not os.path.exists(doc_path): os.makedirs(doc_path)

def unregister():
    pass