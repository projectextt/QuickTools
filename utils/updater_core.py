import bpy, os, shutil, urllib.request, zipfile, json
import addon_utils

# --- CONFIG ---
GITHUB_USER = "projectextt"
GITHUB_REPO = "QuickTools"
TOKEN = "" # Kosongkan jika Public. Isi "ghp_xxx" jika Private.

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

# --- PATHS ---
doc_path = os.path.join(os.path.expanduser("~"), "Documents", "QuickTools", "Blender 4.2", "__updater__")
backup_path = os.path.join(doc_path, "__backup__")
source_path = os.path.join(doc_path, "__source__")

update_available = False
latest_version = ""
download_url = ""

def show_message(message="", title="QuickTools Update", icon='INFO'):
    def draw(self, context): self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def check_for_update():
    global update_available, latest_version, download_url
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url)
        if TOKEN: req.add_header('Authorization', f'token {TOKEN}')
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            tag = data['tag_name'].replace('v', '').replace('update ', '')
            
            # Konversi tag string ke tuple (misal "4.0.9" -> (4,0,9))
            ver_tuple = tuple(map(int, tag.split('.')))
            
            if ver_tuple > CURRENT_VERSION:
                update_available = True
                latest_version = tag
                download_url = data['zipball_url']
                show_message(f"Update Tersedia: v{tag}", title="Update Found")
            else:
                update_available = False
                current_ver_str = ".".join(map(str, CURRENT_VERSION))
                show_message(f"QuickTools v{current_ver_str} sudah versi terbaru.", title="Latest Version")
    except Exception as e:
        show_message(f"Cek Gagal: {str(e)}", title="Error", icon='ERROR')

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
                    os.remove(os.path.join(root, f))
            for d in dirs:
                if d == "__pycache__":
                    shutil.rmtree(os.path.join(root, d))

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
        show_message("Update Sukses! Klik OK untuk menutup Blender dan menerapkan perubahan.", title="Berhasil")
        bpy.ops.quicktools.restart_blender('INVOKE_DEFAULT')
        
    except Exception as e:
        show_message(str(e), title="Update Gagal", icon='ERROR')

def register():
    if not os.path.exists(doc_path): os.makedirs(doc_path)

def unregister():
    pass