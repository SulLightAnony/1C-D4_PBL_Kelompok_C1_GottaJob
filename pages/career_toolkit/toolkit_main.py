import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QScrollArea, 
                             QGridLayout, QFrame, QLineEdit, QTextEdit, 
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import komponen pro dari ui_components
from .data_manager import CVDataManager
from .ui_components import CVCard, ExperienceInputWidget, EducationInputWidget, TemplateCard, CVPreviewWidget
from .pdf_generator import CVRenderer

class CareerToolkitPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = CVDataManager()
        
        self.experience_widgets = []
        self.education_widgets = []
        
        self.current_editing_id = None
        self.temp_form_data = {} 
        self.selected_template = None # Menyimpan ID template sementara
        
        self.init_ui()
        self.check_for_draft()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Inisialisasi Empat Layar Utama
        self.view_dashboard = QWidget()
        self.view_form = QWidget()
        self.view_template_select = QWidget()
        self.view_preview = QWidget() # LAYAR BARU

        self.setup_dashboard_ui()
        self.setup_form_ui()
        self.setup_template_selection_ui()
        self.setup_preview_ui() # SETUP LAYAR BARU

        self.stack.addWidget(self.view_dashboard)        # Index 0
        self.stack.addWidget(self.view_form)             # Index 1
        self.stack.addWidget(self.view_template_select)  # Index 2
        self.stack.addWidget(self.view_preview)          # Index 3

        self.refresh_dashboard()

    # ==========================================
    # 1. UI DASHBOARD
    # ==========================================
    def setup_dashboard_ui(self):
        layout = QVBoxLayout(self.view_dashboard)
        header = QLabel("ATS CV Builder")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header.setStyleSheet("color: #2C687B; margin: 20px;")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setSpacing(25)
        
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)

    def refresh_dashboard(self):
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        btn_add = QPushButton("+")
        btn_add.setFixedSize(220, 280)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFont(QFont("Arial", 48))
        btn_add.setStyleSheet("QPushButton { background-color: #f5f5f5; color: #2C687B; border: 2px dashed #2C687B; border-radius: 10px; }")
        btn_add.clicked.connect(lambda: self.open_form_editor())
        self.grid_layout.addWidget(btn_add, 0, 0)

        all_cv = self.manager.get_all_cv()
        row, col = 0, 1
        for cv_data in all_cv:
            card = CVCard(cv_data)
            card.edit_clicked.connect(self.open_form_editor)
            card.print_clicked.connect(self.handle_print_pdf)
            card.duplicate_clicked.connect(self.handle_duplicate)
            card.delete_clicked.connect(self.handle_delete)
            
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 3: col = 0; row += 1

    # ==========================================
    # 2. UI FORM EDITOR
    # ==========================================
    def setup_form_ui(self):
        layout = QVBoxLayout(self.view_form)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        form_container = QWidget(); self.form_layout = QVBoxLayout(form_container)
        
        self.form_layout.addWidget(QLabel("<b>INFORMASI PRIBADI</b>"))
        self.input_name = QLineEdit(); self.input_name.setPlaceholderText("Nama Lengkap")
        self.input_email = QLineEdit(); self.input_email.setPlaceholderText("Email")
        self.input_phone = QLineEdit(); self.input_phone.setPlaceholderText("Nomor Telepon")
        self.input_linkedin = QLineEdit(); self.input_linkedin.setPlaceholderText("URL LinkedIn")
        for w in [self.input_name, self.input_email, self.input_phone, self.input_linkedin]: self.form_layout.addWidget(w)

        h_ai = QHBoxLayout(); h_ai.addWidget(QLabel("<b>RINGKASAN PROFESIONAL</b>")); h_ai.addStretch()
        btn_ai = QPushButton("✨ Perbagus (AI)"); btn_ai.clicked.connect(self.handle_ai_enhance)
        h_ai.addWidget(btn_ai); self.form_layout.addLayout(h_ai)
        self.input_summary = QTextEdit(); self.input_summary.setFixedHeight(100); self.form_layout.addWidget(self.input_summary)

        self.form_layout.addWidget(QLabel("<br><b>RIWAYAT PENDIDIKAN</b>"))
        self.edu_container = QVBoxLayout(); self.form_layout.addLayout(self.edu_container)
        btn_add_edu = QPushButton("+ Tambah Pendidikan"); btn_add_edu.clicked.connect(lambda: self.add_education_block())
        self.form_layout.addWidget(btn_add_edu)

        self.form_layout.addWidget(QLabel("<br><b>PENGALAMAN KERJA</b>"))
        self.exp_container = QVBoxLayout(); self.form_layout.addLayout(self.exp_container)
        btn_add_exp = QPushButton("+ Tambah Pengalaman"); btn_add_exp.clicked.connect(lambda: self.add_experience_block())
        self.form_layout.addWidget(btn_add_exp)

        self.form_layout.addWidget(QLabel("<br><b>KEAHLIAN (SKILLS)</b>"))
        self.input_skills = QLineEdit(); self.input_skills.setPlaceholderText("Misal: Python, SQL, Project Management (Pisahkan dengan koma)")
        self.form_layout.addWidget(self.input_skills)

        footer = QHBoxLayout(); btn_back = QPushButton("Batal"); btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_next = QPushButton("Selanjutnya: Pilih Desain"); btn_next.setStyleSheet("background-color: #2C687B; color: white; padding: 10px;")
        btn_next.clicked.connect(self.go_to_template_selection)
        footer.addWidget(btn_back); footer.addStretch(); footer.addWidget(btn_next)
        
        scroll.setWidget(form_container); layout.addWidget(scroll); layout.addLayout(footer)

    # ==========================================
    # 3. UI TEMPLATE SELECTION
    # ==========================================
    def setup_template_selection_ui(self):
        layout = QVBoxLayout(self.view_template_select)
        
        header = QLabel("Pilih Desain CV")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(header)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        grid_widget = QWidget(); grid = QGridLayout(grid_widget)
        
        templates = [
            ("ats_classic", "ATS Classic", "Profesional dengan aksen biru."),
            ("ats_modern", "ATS Modern", "Elegan, font serif, teks rata tengah."),
            ("ats_minimalist", "ATS Minimalist", "Bersih, rata kiri, hemat ruang.")
        ]

        col = 0
        for t_id, t_name, t_desc in templates:
            t_card = TemplateCard(t_id, t_name, t_desc)
            # UBAH: Sekarang menuju ke preview, bukan langsung save
            t_card.template_selected.connect(self.go_to_preview) 
            grid.addWidget(t_card, 0, col)
            col += 1

        btn_back = QPushButton("Kembali ke Edit Data")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        layout.addWidget(btn_back)

    # ==========================================
    # 4. UI PREVIEW (LAYAR BARU)
    # ==========================================
    def setup_preview_ui(self):
        layout = QVBoxLayout(self.view_preview)
        
        header = QLabel("Pratinjau CV")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(header)

        # Komponen Preview HTML
        self.preview_widget = CVPreviewWidget()
        layout.addWidget(self.preview_widget)

        # Footer Navigasi
        footer = QHBoxLayout()
        btn_back = QPushButton("← Kembali Pilih Desain")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        
        btn_save = QPushButton("Simpan & Cetak PDF")
        btn_save.setStyleSheet("background-color: #E28F41; color: white; padding: 10px; font-weight: bold;")
        btn_save.clicked.connect(self.finalize_and_save)
        
        footer.addWidget(btn_back)
        footer.addStretch()
        footer.addWidget(btn_save)
        layout.addLayout(footer)

    # ==========================================
    # 5. LOGIKA OPERASIONAL
    # ==========================================
    def open_form_editor(self, cv_id=None):
        self.current_editing_id = cv_id
        for w in self.experience_widgets + self.education_widgets: w.setParent(None)
        self.experience_widgets = []; self.education_widgets = []
        self.input_name.clear(); self.input_email.clear(); self.input_phone.clear(); self.input_linkedin.clear(); self.input_summary.clear(); self.input_skills.clear()

        if cv_id:
            all_cv = self.manager.get_all_cv()
            data = next((item for item in all_cv if item["cv_id"] == cv_id), {})
            self.input_name.setText(data.get("full_name", ""))
            self.input_email.setText(data.get("email", ""))
            self.input_phone.setText(data.get("phone", ""))
            self.input_linkedin.setText(data.get("linkedin", ""))
            self.input_summary.setPlainText(data.get("summary", ""))
            self.input_skills.setText(", ".join(data.get("skills", [])))
            for edu in data.get("education", []): self.add_education_block(edu)
            for exp in data.get("experience", []): self.add_experience_block(exp)
        else:
            self.add_education_block(); self.add_experience_block()

        self.stack.setCurrentIndex(1)

    def add_experience_block(self, data=None):
        block = ExperienceInputWidget(data); block.delete_requested.connect(self.remove_exp)
        self.exp_container.addWidget(block); self.experience_widgets.append(block)

    def remove_exp(self, w): w.setParent(None); self.experience_widgets.remove(w)

    def add_education_block(self, data=None):
        block = EducationInputWidget(data); block.delete_requested.connect(self.remove_edu)
        self.edu_container.addWidget(block); self.education_widgets.append(block)

    def remove_edu(self, w): w.setParent(None); self.education_widgets.remove(w)

    def go_to_template_selection(self):
        if not self.input_name.text():
            QMessageBox.warning(self, "Peringatan", "Nama Lengkap harus diisi!")
            return
        
        skill_list = [s.strip() for s in self.input_skills.text().split(",") if s.strip()]
        self.temp_form_data = {
            "cv_id": self.current_editing_id,
            "cv_name": f"CV {self.input_name.text()}",
            "full_name": self.input_name.text(),
            "email": self.input_email.text(),
            "phone": self.input_phone.text(),
            "linkedin": self.input_linkedin.text(),
            "summary": self.input_summary.toPlainText(),
            "skills": skill_list,
            "education": [w.get_data() for w in self.education_widgets],
            "experience": [w.get_data() for w in self.experience_widgets]
        }
        self.manager.save_to_temp(self.temp_form_data)
        self.stack.setCurrentIndex(2)

    def go_to_preview(self, template_id):
        """Memuat data form ke dalam widget preview."""
        self.selected_template = template_id
        self.preview_widget.render_preview(self.temp_form_data, template_id)
        self.stack.setCurrentIndex(3)

    def finalize_and_save(self):
        """Tahap akhir dari tombol Simpan di layar Preview."""
        if not self.selected_template: return
        
        # 1. Simpan ke database JSON
        self.manager.save_final_cv(self.temp_form_data, self.selected_template)
        
        # 2. Opsional: Beri pilihan user untuk langsung render file PDF ke komputernya
        QMessageBox.information(self, "Berhasil", "Data CV telah disimpan ke Dashboard.")
        self.refresh_dashboard()
        self.stack.setCurrentIndex(0)

    def handle_print_pdf(self, cv_id):
        all_cv = self.manager.get_all_cv()
        data = next((item for item in all_cv if item["cv_id"] == cv_id), None)
        if data:
            path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", f"{data['cv_name']}.pdf", "PDF Files (*.pdf)")
            if path:
                renderer = CVRenderer(data)
                renderer.generate_pdf(path, data.get("template_id", "ats_classic"))
                QMessageBox.information(self, "Sukses", "CV Berhasil dicetak menjadi PDF!")

    def handle_duplicate(self, cv_id):
        if self.manager.duplicate_cv(cv_id): self.refresh_dashboard()

    def handle_delete(self, cv_id):
        if QMessageBox.question(self, 'Konfirmasi', 'Hapus CV ini?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.manager.delete_cv(cv_id); self.refresh_dashboard()

    def handle_ai_enhance(self):
        QMessageBox.information(self, "Info AI", "Fitur 'Perbagus dengan AI' akan segera hadir setelah integrasi selesai!")

    def check_for_draft(self):
        temp = self.manager.get_temp_data()
        if temp and temp.get("full_name"):
            res = QMessageBox.question(self, "Draft Tersedia", "Anda memiliki form yang belum disave. Ingin dilanjutkan?", QMessageBox.Yes | QMessageBox.No)
            if res == QMessageBox.Yes:
                self.open_form_editor(temp.get("cv_id"))