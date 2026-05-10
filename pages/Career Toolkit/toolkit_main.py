import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLabel
from gemini_api import perbagus_teks_cv

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QScrollArea, 
                             QGridLayout, QFrame, QLineEdit, QTextEdit, 
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor

# Import komponen lokal
from data_manager import CVDataManager
from ui_components import (CVCard, ExperienceInputWidget, EducationInputWidget, 
                           OrganizationInputWidget, CertificationInputWidget, 
                           PhotoUploaderWidget, TemplateCard, CVPreviewWidget,
                           CompactInputWidget)
from pdf_generator import CVRenderer

class AIWorker(QThread):
    finished_signal = pyqtSignal(str)
    def __init__(self, job_data, text_to_fix):
        super().__init__()
        self.job_data = job_data
        self.text_to_fix = text_to_fix
        
    def run(self):
        hasil = perbagus_teks_cv(self.job_data, self.text_to_fix)
        self.finished_signal.emit(hasil)

class LoadingAIDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sistem AI Aktif")
        self.setFixedSize(320, 150)
        self.setModal(True) # Cegah user klik apapun
        
        layout = QVBoxLayout(self)
        self.lbl = QLabel("✨ Mengkalibrasi CV Anda...\nMohon tunggu sebentar.", self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.btn_batal = QPushButton("Batalkan", self)
        layout.addWidget(self.lbl)
        layout.addWidget(self.btn_batal)

class CareerToolkitPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = CVDataManager()
        
        # Penampung widget dinamis
        self.experience_widgets = []
        self.education_widgets = []
        self.organization_widgets = []
        self.certification_widgets = []
        self.skills_widgets = []
        self.languages_widgets = []
        
        self.current_editing_id = None
        self.temp_form_data = {} 
        self.selected_template = None 
        
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.view_dashboard = QWidget()
        self.view_form = QWidget()
        self.view_template_select = QWidget()
        self.view_preview = QWidget()

        self.setup_dashboard_ui()
        self.setup_form_ui()
        self.setup_template_selection_ui()
        self.setup_preview_ui()

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
        header.setStyleSheet("color: #2C687B; margin: 20px 20px 0 20px;")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setSpacing(25)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)

    def refresh_dashboard(self):
        # Clear grid
        for i in reversed(range(self.grid_layout.count())): 
            item = self.grid_layout.itemAt(i)
            if item.widget(): item.widget().setParent(None)

        # Tombol Tambah Baru
        btn_add = QPushButton("+")
        btn_add.setFixedSize(220, 280)
        btn_add.setCursor(QCursor(Qt.PointingHandCursor))
        btn_add.setFont(QFont("Arial", 48))
        btn_add.setStyleSheet("""
            QPushButton { background-color: #f1f5f9; color: #2C687B; border: 2px dashed #94a3b8; border-radius: 12px; }
            QPushButton:hover { background-color: #e2e8f0; border: 2px dashed #2C687B; }
        """)
        btn_add.clicked.connect(lambda: self.open_form_editor())
        self.grid_layout.addWidget(btn_add, 0, 0)

        # Load CV dari Database
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
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border: none;")
        form_container = QWidget(); self.form_layout = QVBoxLayout(form_container); self.form_layout.setSpacing(15)
        
        # --- INFO PRIBADI & FOTO ---
        self.form_layout.addWidget(QLabel("<b>INFORMASI PRIBADI & FOTO</b>"))
        self.photo_uploader = PhotoUploaderWidget()
        self.form_layout.addWidget(self.photo_uploader)

        self.input_name = QLineEdit(); self.input_name.setPlaceholderText("Nama Lengkap")
        self.input_email = QLineEdit(); self.input_email.setPlaceholderText("Email")
        self.input_phone = QLineEdit(); self.input_phone.setPlaceholderText("Nomor Telepon")
        self.input_linkedin = QLineEdit(); self.input_linkedin.setPlaceholderText("URL LinkedIn / Portofolio")
        
        for w in [self.input_name, self.input_email, self.input_phone, self.input_linkedin]: 
            w.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 5px;")
            self.form_layout.addWidget(w)

        # STYLE AI DENGAN FONT 12PX (LEBIH BESAR)
        style_ai_btn = "background-color: #e0e7ff; color: #4338ca; border-radius: 12px; padding: 5px 15px; font-weight: bold; font-size: 12px;"

        # --- SEKSI-SEKSI DENGAN AI ENHANCE ---
        sections = [
            ("RINGKASAN PROFESIONAL", "summary", self.handle_ai_enhance),
            ("PENGALAMAN KERJA", "experience", self.handle_ai_enhance),
            ("PENGALAMAN ORGANISASI / VOLUNTEER", "organization", self.handle_ai_enhance),
            ("SERTIFIKASI & PENGHARGAAN", "certification", self.handle_ai_enhance)
        ]
        
        self.ai_buttons = {}
        self.toggle_buttons = {}

        for title, target, func in sections:
            h_header = QHBoxLayout()
            h_header.addWidget(QLabel(f"<br><b>{title}</b>"))
            h_header.addStretch()
            
            # --- TOMBOL TOGGLE (Langkah 4) ---
            # Kita buat tersembunyi dulu, baru muncul kalau AI selesai dipakai
            btn_toggle = QPushButton("Lihat Teks Asli")
            btn_toggle.setVisible(False) 
            btn_toggle.setStyleSheet("background-color: #6c757d; color: white; border-radius: 5px; padding: 5px 10px;")
            self.toggle_buttons[target] = btn_toggle
            h_header.addWidget(btn_toggle)

            # --- TOMBOL AI ---
            btn_ai = QPushButton("Perbagus")
            btn_ai.setCursor(QCursor(Qt.PointingHandCursor))
            # Gunakan style_ai_btn milikmu
            btn_ai.setStyleSheet("background-color: #2980B9; color: white; border-radius: 5px; padding: 5px 10px;") 
            self.ai_buttons[target] = btn_ai
            h_header.addWidget(btn_ai)
            
            self.form_layout.addLayout(h_header)
            
            # Koneksikan tombol ke fungsinya masing-masing
            btn_ai.clicked.connect(lambda checked, t=target: self.handle_ai_enhance(t))
            btn_toggle.clicked.connect(lambda checked, t=target: self.handle_toggle_teks(t))
            
            if target == "summary":
                self.input_summary = QTextEdit(); self.input_summary.setFixedHeight(100)
                self.input_summary.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 5px;")
                self.form_layout.addWidget(self.input_summary)
            elif target == "experience":
                self.exp_container = QVBoxLayout(); self.form_layout.addLayout(self.exp_container)
                btn_add = QPushButton("+ Tambah Pengalaman"); btn_add.setCursor(QCursor(Qt.PointingHandCursor))
                btn_add.setStyleSheet("padding: 8px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 5px;")
                btn_add.clicked.connect(lambda: self.add_dynamic_block("experience"))
                self.form_layout.addWidget(btn_add)
            elif target == "organization":
                self.org_container = QVBoxLayout(); self.form_layout.addLayout(self.org_container)
                btn_add = QPushButton("+ Tambah Organisasi"); btn_add.setCursor(QCursor(Qt.PointingHandCursor))
                btn_add.setStyleSheet("padding: 8px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 5px;")
                btn_add.clicked.connect(lambda: self.add_dynamic_block("organization"))
                self.form_layout.addWidget(btn_add)
            elif target == "certification":
                self.cert_container = QVBoxLayout(); self.form_layout.addLayout(self.cert_container)
                btn_add = QPushButton("+ Tambah Sertifikasi"); btn_add.setCursor(QCursor(Qt.PointingHandCursor))
                btn_add.setStyleSheet("padding: 8px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 5px;")
                btn_add.clicked.connect(lambda: self.add_dynamic_block("certification"))
                self.form_layout.addWidget(btn_add)

        # --- PENDIDIKAN, SERTIFIKASI, SKILLS, BAHASA ---
        self.form_layout.addWidget(QLabel("<br><b>RIWAYAT PENDIDIKAN</b>"))
        self.edu_container = QVBoxLayout(); self.form_layout.addLayout(self.edu_container)
        btn_add_edu = QPushButton("+ Tambah Pendidikan"); btn_add_edu.clicked.connect(lambda: self.add_dynamic_block("education"))
        self.form_layout.addWidget(btn_add_edu)

        self.form_layout.addWidget(QLabel("<br><b>KEAHLIAN / ALAT</b>"))
        self.skills_container = QVBoxLayout(); self.form_layout.addLayout(self.skills_container)
        btn_add_skill = QPushButton("+ Tambah Keahlian"); btn_add_skill.clicked.connect(lambda: self.add_dynamic_block("skill"))
        self.form_layout.addWidget(btn_add_skill)

        self.form_layout.addWidget(QLabel("<br><b>BAHASA</b>"))
        self.lang_container = QVBoxLayout(); self.form_layout.addLayout(self.lang_container)
        btn_add_lang = QPushButton("+ Tambah Bahasa"); btn_add_lang.clicked.connect(lambda: self.add_dynamic_block("language"))
        self.form_layout.addWidget(btn_add_lang)
        
        # Tambahkan styling pada semua tombol tambah
        for i in range(self.form_layout.count()):
            w = self.form_layout.itemAt(i).widget()
            if isinstance(w, QPushButton) and "+" in w.text():
                w.setCursor(QCursor(Qt.PointingHandCursor))
                w.setStyleSheet("padding: 8px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 5px;")

        # --- FOOTER NAVIGASI (DENGAN TOMBOL EDIT/SIMPAN PERUBAHAN) ---
        footer = QHBoxLayout(); footer.setContentsMargins(0, 20, 0, 10)
        btn_back = QPushButton("Batal"); btn_back.setCursor(QCursor(Qt.PointingHandCursor))
        btn_back.setStyleSheet("padding: 10px 20px; border: 1px solid #cbd5e1; border-radius: 6px;")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        # TOMBOL SIMPAN PERUBAHAN (HANYA MUNCUL DI MODE EDIT)
        self.btn_direct_save = QPushButton("Simpan Perubahan")
        self.btn_direct_save.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_direct_save.setStyleSheet("background-color: #E28F41; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        self.btn_direct_save.clicked.connect(self.save_changes_direct)
        self.btn_direct_save.hide() # Sembunyikan default
        
        btn_next = QPushButton("Selanjutnya"); btn_next.setCursor(QCursor(Qt.PointingHandCursor))
        btn_next.setStyleSheet("background-color: #2C687B; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        btn_next.clicked.connect(self.go_to_template_selection)
        
        footer.addWidget(btn_back); footer.addStretch(); footer.addWidget(self.btn_direct_save); footer.addWidget(btn_next)
        
        scroll.setWidget(form_container); layout.addWidget(scroll); layout.addLayout(footer)

    # ==========================================
    # 3. LOGIKA OPERASIONAL
    # ==========================================
    def open_form_editor(self, cv_id=None):
        self.current_editing_id = cv_id
        
        # Munculkan tombol simpan perubahan jika mengedit CV lama
        if cv_id: self.btn_direct_save.show()
        else: self.btn_direct_save.hide()
        
        # Bersihkan form
        for w_list in [self.experience_widgets, self.education_widgets, self.organization_widgets, 
                       self.certification_widgets, self.skills_widgets, self.languages_widgets]:
            for w in w_list: w.setParent(None)
            w_list.clear()
            
        self.input_name.clear(); self.input_email.clear(); self.input_phone.clear()
        self.input_linkedin.clear(); self.input_summary.clear()
        self.photo_uploader.remove_image()
        self.reset_ai_states()
        
        if cv_id:
            all_cv = self.manager.get_all_cv()
            data = next((item for item in all_cv if item["cv_id"] == cv_id), {})
            
            if "photo" in data: self.photo_uploader.init_ui(data["photo"])
            self.input_name.setText(data.get("full_name", ""))
            self.input_email.setText(data.get("email", ""))
            self.input_phone.setText(data.get("phone", ""))
            self.input_linkedin.setText(data.get("linkedin", ""))
            self.input_summary.setPlainText(data.get("summary", ""))
            self.selected_template = data.get("template_id", "ats_classic")
            
            for exp in data.get("experience", []): self.add_dynamic_block("experience", exp)
            for edu in data.get("education", []): self.add_dynamic_block("education", edu)
            for org in data.get("organizations", []): self.add_dynamic_block("organization", org)
            for cert in data.get("certifications", []): self.add_dynamic_block("certification", cert)
            for skill in data.get("skills", []): self.add_dynamic_block("skill", skill)
            for lang in data.get("languages", []): self.add_dynamic_block("language", lang)
        else:
            # Isi default untuk CV baru
            self.add_dynamic_block("education"); self.add_dynamic_block("experience")
            self.add_dynamic_block("skill"); self.add_dynamic_block("language")

        self.stack.setCurrentIndex(1)

    def save_changes_direct(self):
        """Menyimpan data langsung ke JSON tanpa harus memilih template ulang."""
        if not self.input_name.text():
            QMessageBox.warning(self, "Peringatan", "Nama Lengkap harus diisi!")
            return
            
        self.gather_form_data()
        self.manager.save_final_cv(self.temp_form_data, self.selected_template)
        
        # Kembali ke Dashboard dengan silent save
        self.refresh_dashboard()
        self.stack.setCurrentIndex(0)

    def gather_form_data(self):
        """Mengumpulkan semua input dari form ke dalam dictionary temp_form_data."""
        skill_list = [w.get_data() for w in self.skills_widgets if w.get_data().strip()]
        lang_list = [w.get_data() for w in self.languages_widgets if w.get_data().strip()]
        
        self.temp_form_data = {
            "cv_id": self.current_editing_id,
            "cv_name": f"CV {self.input_name.text()}",
            "photo": self.photo_uploader.get_data(),
            "full_name": self.input_name.text(),
            "email": self.input_email.text(),
            "phone": self.input_phone.text(),
            "linkedin": self.input_linkedin.text(),
            "summary": self.input_summary.toPlainText(),
            "skills": skill_list,
            "languages": lang_list,
            "education": [w.get_data() for w in self.education_widgets],
            "experience": [w.get_data() for w in self.experience_widgets],
            "organizations": [w.get_data() for w in self.organization_widgets],
            "certifications": [w.get_data() for w in self.certification_widgets]
        }

    def go_to_template_selection(self):
        if not self.input_name.text():
            QMessageBox.warning(self, "Peringatan", "Nama Lengkap harus diisi!")
            return
        self.gather_form_data()
        self.manager.save_to_temp(self.temp_form_data)
        self.stack.setCurrentIndex(2)

    def finalize_and_save(self):
        """Fungsi akhir: Simpan ke JSON dan langsung trigger simpan PDF."""
        if not self.selected_template: return
        
        self.manager.save_final_cv(self.temp_form_data, self.selected_template)
        
        cv_name = self.temp_form_data.get("cv_name", "Curriculum_Vitae")
        path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", f"{cv_name}.pdf", "PDF Files (*.pdf)")
        if path:
            self.temp_form_data["template_id"] = self.selected_template
            renderer = CVRenderer(self.temp_form_data)
            renderer.generate_pdf(path, self.selected_template)

        self.refresh_dashboard()
        self.stack.setCurrentIndex(0)

    # ==========================================
    # LOGIKA LAIN (DYNAMIC BLOCKS & AI)
    # ==========================================
    def add_dynamic_block(self, block_type, data=None):
        if block_type == "experience":
            block = ExperienceInputWidget(data); block.delete_requested.connect(lambda w: self.remove_dynamic_block(w, self.experience_widgets))
            self.exp_container.addWidget(block); self.experience_widgets.append(block)
        elif block_type == "education":
            block = EducationInputWidget(data); block.delete_requested.connect(lambda w: self.remove_dynamic_block(w, self.education_widgets))
            self.edu_container.addWidget(block); self.education_widgets.append(block)
        elif block_type == "organization":
            block = OrganizationInputWidget(data); block.delete_requested.connect(lambda w: self.remove_dynamic_block(w, self.organization_widgets))
            self.org_container.addWidget(block); self.organization_widgets.append(block)
        elif block_type == "certification":
            block = CertificationInputWidget(data); block.delete_requested.connect(lambda w: self.remove_dynamic_block(w, self.certification_widgets))
            self.cert_container.addWidget(block); self.certification_widgets.append(block)
        elif block_type == "skill":
            block = CompactInputWidget("Misal: Python, SQL", data); block.delete_requested.connect(lambda w: self.remove_dynamic_block(w, self.skills_widgets))
            self.skills_container.addWidget(block); self.skills_widgets.append(block)
        elif block_type == "language":
            block = CompactInputWidget("Misal: Bahasa Inggris (Aktif)", data); block.delete_requested.connect(lambda w: self.remove_dynamic_block(w, self.languages_widgets))
            self.lang_container.addWidget(block); self.languages_widgets.append(block)

    def remove_dynamic_block(self, widget, widget_list):
        widget.setParent(None); widget_list.remove(widget)

    def setup_template_selection_ui(self):
        layout = QVBoxLayout(self.view_template_select)
        header = QLabel("Pilih Desain CV"); header.setFont(QFont("Segoe UI", 18, QFont.Bold)); layout.addWidget(header)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border: none;")
        grid_widget = QWidget(); grid = QGridLayout(grid_widget); grid.setSpacing(20)
        templates = [
            ("ats_classic", "ATS Classic", "Profesional dengan aksen biru.", "CV-01.png"),
            ("ats_modern", "ATS Modern", "Elegan, font serif, rata tengah.", "CV-02.png"),
            ("ats_minimalist", "ATS Minimalist", "Bersih, rata kiri, hemat ruang.", "CV-03.png")
        ]
        col = 0
        for t_id, t_name, t_desc, t_img in templates:
            t_card = TemplateCard(t_id, t_name, t_desc, t_img)
            t_card.template_selected.connect(self.go_to_preview); grid.addWidget(t_card, 0, col); col += 1
        
        btn_back = QPushButton("← Kembali ke Edit Data"); btn_back.setStyleSheet("padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px;"); btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        scroll.setWidget(grid_widget); layout.addWidget(scroll); layout.addWidget(btn_back)

    def setup_preview_ui(self):
        layout = QVBoxLayout(self.view_preview)
        header = QLabel("Pratinjau CV"); header.setFont(QFont("Segoe UI", 18, QFont.Bold)); layout.addWidget(header)
        self.preview_widget = CVPreviewWidget(); layout.addWidget(self.preview_widget)
        footer = QHBoxLayout(); btn_back = QPushButton("← Kembali Pilih Desain"); btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        
        # --- PERUBAHAN TEKS TOMBOL ---
        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("background-color: #E28F41; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        btn_save.clicked.connect(self.finalize_and_save)
        
        footer.addWidget(btn_back); footer.addStretch(); footer.addWidget(btn_save); layout.addLayout(footer)

    def go_to_preview(self, template_id):
        self.selected_template = template_id; self.preview_widget.render_preview(self.temp_form_data, template_id); self.stack.setCurrentIndex(3)

    def handle_print_pdf(self, cv_id):
        all_cv = self.manager.get_all_cv()
        data = next((item for item in all_cv if item["cv_id"] == cv_id), None)
        if data:
            path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", f"{data['cv_name']}.pdf", "PDF Files (*.pdf)")
            if path:
                renderer = CVRenderer(data); renderer.generate_pdf(path, data.get("template_id", "ats_classic"))

    def handle_duplicate(self, cv_id):
        if self.manager.duplicate_cv(cv_id): self.refresh_dashboard()

    def handle_delete(self, cv_id):
        if QMessageBox.question(self, 'Konfirmasi', 'Hapus CV ini?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.manager.delete_cv(cv_id); self.refresh_dashboard()

    def handle_ai_enhance(self, target_section):
        # 1. TEMUKAN WIDGET YANG TEPAT
        widget_target = self.get_target_widget(target_section)
        if not widget_target:
            QMessageBox.warning(self, "Data Kosong", f"Silakan isi data {target_section} terlebih dahulu!")
            return

        if target_section == "summary":
            widget_target = self.input_summary
        elif target_section == "experience":
            if not self.experience_widgets:
                QMessageBox.warning(self, "Kosong", "Tambahkan pengalaman kerja dulu!")
                return
            widget_target = self.experience_widgets[0].input_desc # Mengambil pengalaman teratas
        elif target_section == "organization":
            if not self.organization_widgets:
                QMessageBox.warning(self, "Kosong", "Tambahkan organisasi dulu!")
                return
            widget_target = self.organization_widgets[0].input_desc

        teks_asli = widget_target.toPlainText().strip()
        if not teks_asli:
            QMessageBox.warning(self, "Teks Kosong", "Ketik draf kasarnya dulu ya!")
            return

        # 2. SIMPAN TEKS ASLI UNTUK FITUR TOGGLE
        if not hasattr(widget_target, 'teks_orisinal'):
            widget_target.teks_orisinal = teks_asli
        
        # 3. KUNCI SEMUA TOMBOL (Anti Spam)
        btn_ai_aktif = self.ai_buttons[target_section]
        btn_ai_aktif.setText("Memperbagus...")
        
        for btn in self.ai_buttons.values():
            btn.setEnabled(False) # Matikan semua tombol AI

        # 4. JALANKAN AI DI BACKGROUND THREAD
        job_info = getattr(self, 'target_job', None)
        self.ai_thread = AIWorker(job_info, teks_asli)
        
        def on_ai_finished(hasil):
            # Timpa teks dengan hasil AI
            widget_target.setPlainText(hasil)
            widget_target.teks_hasil_ai = hasil # Simpan data hasil AI untuk toggle
            
            # Munculkan Tombol Toggle
            btn_toggle = self.toggle_buttons[target_section]
            btn_toggle.setVisible(True)
            btn_toggle.setText("Lihat Teks Asli")
            btn_toggle.is_showing_ai = True
            
            # Buka kembali kunci tombol AI
            for btn in self.ai_buttons.values():
                btn.setEnabled(True)
            btn_ai_aktif.setText("Perbagus")

        self.ai_thread.finished_signal.connect(on_ai_finished)
        self.ai_thread.start()

    def handle_toggle_teks(self, target_section):
        widget_target = self.get_target_widget(target_section)
        btn_toggle = self.toggle_buttons.get(target_section)
        
        if not widget_target or not btn_toggle:
            return

        # Validasi ketat: Cegah eksekusi jika atribut belum dibuat oleh AI
        if not hasattr(widget_target, 'teks_orisinal') or not hasattr(widget_target, 'teks_hasil_ai'):
            btn_toggle.setVisible(False)
            return

        # Gunakan getattr untuk menghindari error jika status is_showing_ai belum diset
        if getattr(btn_toggle, 'is_showing_ai', True):
            widget_target.setPlainText(widget_target.teks_orisinal)
            btn_toggle.setText("Lihat Hasil")
            btn_toggle.setStyleSheet("background-color: #27AE60; color: white; border-radius: 5px; padding: 5px 10px;")
            btn_toggle.is_showing_ai = False
        else:
            widget_target.setPlainText(widget_target.teks_hasil_ai)
            btn_toggle.setText("Lihat Teks Asli")
            btn_toggle.setStyleSheet("background-color: #6c757d; color: white; border-radius: 5px; padding: 5px 10px;")
            btn_toggle.is_showing_ai = True
            
    def apply_ai_enhancement(self, job_data):
        self.target_job = job_data
        judul = job_data.get("Judul_Pekerjaan", "Pekerjaan")
        kualifikasi = job_data.get("Kualifikasi_Persyaratan", "").replace("|", ", ")
        
        self.reset_ai_states()
        self.input_summary.clear()
        
        # Reset state untuk summary agar tidak ada teks hantu
        self.input_summary.clear()
        if hasattr(self.input_summary, 'teks_orisinal'):
            delattr(self.input_summary, 'teks_orisinal')
        self.toggle_buttons["summary"].setVisible(False)
        
        self.stack.setCurrentIndex(1)
        
        draf_awal = f"Berpengalaman dalam bidang {judul}. Memiliki keahlian utama dalam: {kualifikasi}."
        
        self.loading_dialog = LoadingAIDialog(self)
        
        def batalkan_proses():
            if hasattr(self, 'auto_ai_thread'):
                self.auto_ai_thread.terminate()
            self.loading_dialog.reject()
            # Gunakan variabel stack yang sudah Anda perbaiki di main.py
            self.window().stack.setCurrentIndex(0) 
            
        self.loading_dialog.btn_batal.clicked.connect(batalkan_proses)
        
        self.auto_ai_thread = AIWorker(self.target_job, draf_awal)
        
        def on_auto_ai_finished(hasil):
            self.loading_dialog.accept()
            self.input_summary.setPlainText(hasil)
            
            # Simpan data untuk fitur toggle
            self.input_summary.teks_orisinal = draf_awal
            self.input_summary.teks_hasil_ai = hasil
            
            btn_toggle = self.toggle_buttons["summary"]
            btn_toggle.setVisible(True)
            btn_toggle.setText("Lihat Teks Asli")
            btn_toggle.is_showing_ai = True

        self.auto_ai_thread.finished_signal.connect(on_auto_ai_finished)
        self.auto_ai_thread.start()
        self.loading_dialog.exec_()
        
    def get_target_widget(self, target_section):
        """Fungsi pembantu agar tidak menulis ulang logika pencarian widget"""
        if target_section == "summary":
            return self.input_summary
        elif target_section == "experience":
            return self.experience_widgets[0].input_desc if self.experience_widgets else None
        elif target_section == "organization":
            return self.organization_widgets[0].input_desc if self.organization_widgets else None
        elif target_section == "certification":
            # Menargetkan input deskripsi pada sertifikasi pertama
            return self.certification_widgets[0].input_desc if self.certification_widgets else None
        return None
    
    def reset_ai_states(self):
        """Menyembunyikan semua tombol toggle dan menghapus riwayat teks AI sebelumnya."""
        for section, btn in getattr(self, 'toggle_buttons', {}).items():
            btn.setVisible(False)
            widget = self.get_target_widget(section)
            if widget:
                if hasattr(widget, 'teks_orisinal'):
                    delattr(widget, 'teks_orisinal')
                if hasattr(widget, 'teks_hasil_ai'):
                    delattr(widget, 'teks_hasil_ai')
        
class LoadingAIDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Memproses Data")
        self.setFixedSize(300, 150)
        self.setModal(True) # Cegah klik sembarangan di belakang popup
        
        layout = QVBoxLayout(self)
        self.lbl = QLabel("Sedang membuat CV...", self)
        self.lbl.setAlignment(Qt.AlignCenter)
        
        self.btn_batal = QPushButton("Batalkan", self)
        
        layout.addWidget(self.lbl)
        layout.addWidget(self.btn_batal)