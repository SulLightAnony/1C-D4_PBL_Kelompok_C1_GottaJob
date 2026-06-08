import sys
import os
import subprocess
import shutil
import json

def _ensure_database_structure():
    """
    Memastikan seluruh struktur folder database dan file JSON penting
    sudah ada sebelum aplikasi dijalankan.
    Dipanggil sekali saat startup — aman dijalankan berulang kali.
    """
    if getattr(sys, 'frozen', False):
        root = os.path.dirname(sys.executable)
    else:
        root = os.path.dirname(os.path.abspath(__file__))

    # Salin kamus skill default dari bundle jika berjalan di mode frozen dan folder di luar belum berisi file
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dict_path = os.path.join(sys._MEIPASS, "database", "Database Permanen", "Skill Dictionary")
        target_dict_path = os.path.join(root, "database", "Database Permanen", "Skill Dictionary")
        if os.path.exists(bundle_dict_path) and not os.path.exists(os.path.join(target_dict_path, "universal.json")):
            try:
                shutil.copytree(bundle_dict_path, target_dict_path, dirs_exist_ok=True)
            except Exception as e:
                print(f"[WARN] Gagal menyalin default Skill Dictionary: {e}")

    # Daftar folder yang wajib ada
    required_dirs = [
        os.path.join(root, "database", "Database Permanen", "Account Manager"),
        os.path.join(root, "database", "Database Permanen", "Job Archive"),
        os.path.join(root, "database", "Database Permanen", "Favorit"),
        os.path.join(root, "database", "Database Permanen", "Dashboard"),
        os.path.join(root, "database", "Database Permanen", "Skill Dictionary"),
        os.path.join(root, "database", "Database Sementara"),
    ]

    for d in required_dirs:
        os.makedirs(d, exist_ok=True)

    # File JSON yang wajib ada dengan isi default jika belum ada
    required_files = {
        os.path.join(root, "database", "Database Permanen", "Account Manager", "user.json"): [
            {
                "username": "admin",
                "password": "admin1234",
                "role": "admin"
            }
        ],
        os.path.join(root, "database", "Database Permanen", "Dashboard", "aktivitas_user.json"): [],
        os.path.join(root, "database", "Database Permanen", "Dashboard", "aktivitas_admin.json"): [],
    }

    for file_path, default_content in required_files.items():
        is_empty = False
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if not content:  # jika data berupa [] atau {} kosong
                        is_empty = True
            except Exception:
                is_empty = True

        if not os.path.exists(file_path) or is_empty:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(default_content, f, indent=4)
            except OSError as e:
                print(f"[WARN] Tidak bisa membuat/menulis {file_path}: {e}")

# Pastikan struktur database dibuat SEBELUM import AppRouter (agar modul_kategorisasi membaca data yang valid)
try:
    _ensure_database_structure()
except Exception as e:
    print(f"[WARN] _ensure_database_structure error di awal: {e}")

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QProgressBar, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import Router Aplikasi
from app_router import AppRouter

def _get_python_executable():
    """
    Mengembalikan path Python interpreter yang valid untuk digunakan
    pada subprocess. Ketika di-freeze oleh PyInstaller, sys.executable
    adalah GottaJob.exe (bukan python.exe), sehingga harus dicari secara manual.
    """
    if not getattr(sys, 'frozen', False):
        # Mode development: sys.executable sudah python.exe
        return sys.executable
    
    # Mode frozen (PyInstaller): cari python.exe di PATH atau lokasi umum
    python_exe = shutil.which("python") or shutil.which("python3")
    if python_exe:
        return python_exe
    
    # Fallback ke lokasi instalasi Python default di Windows
    for candidate in [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python313", "python.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python312", "python.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python311", "python.exe"),
        r"C:\Python313\python.exe",
        r"C:\Python312\python.exe",
    ]:
        if os.path.isfile(candidate):
            return candidate
    
    return None  # Tidak ditemukan

def _get_flag_file_path():
    """
    Mengembalikan path file flag instalasi Chromium.
    Selalu menggunakan AppData/Local/GottaJob agar dapat ditulis
    baik dalam mode development maupun setelah di-freeze.
    """
    app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    flag_dir = os.path.join(app_data, "GottaJob")
    os.makedirs(flag_dir, exist_ok=True)
    return os.path.join(flag_dir, ".playwright_installed")

class InstallChromiumThread(QThread):
    finished_sig = pyqtSignal(bool, str)
    
    def __init__(self, flag_file, python_exe):
        super().__init__()
        self.flag_file = flag_file
        self.python_exe = python_exe
        
    def run(self):
        try:
            if not self.python_exe:
                self.finished_sig.emit(
                    False,
                    "Python interpreter tidak ditemukan. Tidak dapat menginstal Chromium."
                )
                return
            
            # Jalankan instalasi chromium menggunakan Python interpreter yang tepat
            result = subprocess.run(
                [self.python_exe, "-m", "playwright", "install", "chromium"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Tulis flag agar instalasi tidak diulang pada sesi berikutnya
                with open(self.flag_file, "w") as f:
                    f.write("installed")
                self.finished_sig.emit(True, "")
            else:
                self.finished_sig.emit(False, result.stderr or "Unknown error code")
        except Exception as e:
            self.finished_sig.emit(False, str(e))

def check_and_install_chromium():
    """
    Mengecek apakah Chromium sudah pernah diinstal. Jika belum,
    tampilkan dialog progress dan install menggunakan thread terpisah.
    Flag disimpan di AppData/Local/GottaJob/.playwright_installed.
    """
    flag_file = _get_flag_file_path()
    
    if os.path.exists(flag_file):
        # Sudah pernah diinstal sebelumnya, lewati
        return

    python_exe = _get_python_executable()

    dialog = QDialog()
    dialog.setWindowTitle("Menyiapkan Sistem")
    dialog.setFixedSize(450, 150)
    # Menghilangkan tombol close agar user tidak menginterupsi instalasi penting
    dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
    dialog.setStyleSheet("""
        QDialog { background-color: #F3F4F6; }
        QLabel { color: #1E3A4A; font-size: 14px; font-family: 'Segoe UI'; }
        QProgressBar {
            border: 2px solid #B2D2D9;
            border-radius: 5px;
            text-align: center;
            background-color: white;
        }
        QProgressBar::chunk {
            background-color: #2C687B;
        }
    """)
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(30, 20, 30, 20)
    layout.setSpacing(15)
    
    lbl = QLabel("Menyiapkan engine pencarian (Chromium) untuk pertama kalinya.\nMohon tunggu, ini memerlukan beberapa menit...")
    lbl.setAlignment(Qt.AlignCenter)
    
    progress = QProgressBar()
    progress.setRange(0, 0)  # Animasi loading berputar/marquee
    
    layout.addWidget(lbl)
    layout.addWidget(progress)
    
    thread = InstallChromiumThread(flag_file, python_exe)
    
    def on_finished(success, err):
        dialog.accept()
        if not success:
            QMessageBox.warning(
                None, 
                "Instalasi Gagal", 
                f"Gagal menginstal browser Chromium:\n{err}\n\nFitur pencarian live mungkin tidak akan berfungsi dengan benar."
            )
            # Tetap tulis flag agar tidak muncul terus-menerus di setiap buka aplikasi
            try:
                with open(flag_file, "w") as f:
                    f.write("failed")
            except Exception:
                pass
            
    thread.finished_sig.connect(on_finished)
    thread.start()
    dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Jalankan pengecekan dan instalasi Chromium (hanya sekali)
    check_and_install_chromium()
    
    # Terapkan gaya/styling global jika tersedia
    try:
        from Modul.modul_antarmuka_pengguna import GLOBAL_DIALOG_STYLE
        app.setStyleSheet(GLOBAL_DIALOG_STYLE)
    except ImportError:
        pass
        
    app.setFont(QFont("Segoe UI", 10))
    
    # Inisialisasi router utama aplikasi
    router = AppRouter()
    router.showMaximized()
    
    # Eksekusi event loop aplikasi
    sys.exit(app.exec_())