import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QProgressBar, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import Router Aplikasi
from app_router import AppRouter

class InstallChromiumThread(QThread):
    finished_sig = pyqtSignal(bool, str)
    
    def __init__(self, flag_file):
        super().__init__()
        self.flag_file = flag_file
        
    def run(self):
        try:
            # Jalankan instalasi chromium secara headless
            result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True, text=True)
            if result.returncode == 0:
                with open(self.flag_file, "w") as f:
                    f.write("installed")
                self.finished_sig.emit(True, "")
            else:
                self.finished_sig.emit(False, result.stderr or "Unknown error code")
        except Exception as e:
            self.finished_sig.emit(False, str(e))

def check_and_install_chromium():
    app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    flag_file = os.path.join(app_dir, ".playwright_installed")
    
    if os.path.exists(flag_file):
        return

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
    progress.setRange(0, 0) # Animasi loading berputar/marquee
    
    layout.addWidget(lbl)
    layout.addWidget(progress)
    
    thread = InstallChromiumThread(flag_file)
    
    def on_finished(success, err):
        dialog.accept()
        if not success:
            QMessageBox.critical(
                None, 
                "Instalasi Gagal", 
                f"Gagal menginstal browser Chromium:\n{err}\n\nFitur pencarian live mungkin tidak akan berfungsi dengan benar."
            )
            
    thread.finished_sig.connect(on_finished)
    thread.start()
    dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Jalankan pengecekan dan instalasi Chromium
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