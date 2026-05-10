import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

# Import Router Aplikasi
from app_router import AppRouter

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
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