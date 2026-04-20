# pages/dashboard.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Di sini nanti kamu buat UI Dashboard yang ada grafik/kartu itu
        self.label = QLabel("INI HALAMAN DARI FILE DASHBOARD.PY")
        layout.addWidget(self.label)