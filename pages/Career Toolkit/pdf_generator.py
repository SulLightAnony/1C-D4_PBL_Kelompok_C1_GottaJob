import os
from fpdf import FPDF

class ATS_PDF(FPDF):
    def footer(self):
        """Membuat nomor halaman otomatis di bagian bawah."""
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Halaman {self.page_no()}", align="C")

class CVRenderer:
    def __init__(self, cv_data):
        self.data = cv_data
        self.pdf = ATS_PDF(orientation="P", unit="mm", format="A4")
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        
        # Default Styling (ATS Classic)
        self.font_main = "helvetica"
        self.color_black = (0, 0, 0)
        self.color_gray = (60, 60, 60)
        self.color_accent = (44, 104, 123) # Biru GottaJob
        self.show_line = True
        self.header_align = "C"

    def _apply_template_style(self, template_id):
        """Menyesuaikan gaya visual berdasarkan desain yang dipilih."""
        if template_id == "ats_modern":
            self.font_main = "times"
            self.color_accent = (0, 0, 0) # Hitam murni
            self.show_line = True
            self.header_align = "C"
        elif template_id == "ats_minimalist":
            self.font_main = "helvetica"
            self.color_accent = (200, 200, 200) # Garis tipis abu-abu
            self.show_line = False
            self.header_align = "L" # Rata kiri untuk minimalis
        else: # ats_classic
            self.font_main = "helvetica"
            self.color_accent = (44, 104, 123)
            self.show_line = True
            self.header_align = "C"

    def generate_pdf(self, output_path, template_id="ats_classic"):
        self._apply_template_style(template_id)
        
        # Urutan render ATS standar
        self._render_header_and_photo()
        
        if self.data.get("summary"):
            self._render_section_title("RINGKASAN PROFESIONAL")
            self._render_summary()
            
        if self.data.get("education"):
            self._render_section_title("RIWAYAT PENDIDIKAN")
            self._render_education()

        if self.data.get("experience"):
            self._render_section_title("PENGALAMAN KERJA")
            self._render_experience()

        if self.data.get("organizations"):
            self._render_section_title("PENGALAMAN ORGANISASI")
            self._render_organization()

        if self.data.get("certifications"):
            self._render_section_title("SERTIFIKASI & PENGHARGAAN")
            self._render_certification()

        if self.data.get("skills"):
            self._render_section_title("KEAHLIAN / ALAT")
            self._render_skills()

        if self.data.get("languages"):
            self._render_section_title("BAHASA")
            self._render_languages()

        # Pastikan folder penyimpanan tersedia
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.pdf.output(output_path)
        return output_path

    # ==========================================
    # LOGIKA RENDER KOMPONEN
    # ==========================================

    def _render_header_and_photo(self):
        """Merender info kontak dan menyisipkan foto jika ada."""
        photo_data = self.data.get("photo", {})
        photo_path = photo_data.get("path", "")
        photo_ratio = photo_data.get("ratio", "3x4")
        
        img_w = 0 # Ruang toleransi lebar jika ada foto
        
        # Render Foto jika path valid
        if photo_path and os.path.exists(photo_path):
            try:
                # Kalkulasi rasio fisik (dalam mm absolut)
                img_width_mm = 30 # Base lebar = 3cm
                img_height_mm = 45 if photo_ratio == "2x3" else 40 # Tinggi 4.5cm atau 4.0cm
                
                # Posisi di pojok kanan atas (Kertas A4 lebar 210mm, margin kanan 15mm)
                img_x = 210 - 15 - img_width_mm
                img_y = 15 # Sama dengan top margin
                
                self.pdf.image(photo_path, x=img_x, y=img_y, w=img_width_mm, h=img_height_mm)
                img_w = img_width_mm + 10 # Jarak ekstra 10mm agar teks tidak menabrak pinggiran foto
            except Exception as e:
                print(f"Error merender foto: {e}")

        # Lebar area teks (Full width 180mm dikurangi ruang foto jika ada)
        text_width = 180 - img_w 

        # Nama Lengkap
        self.pdf.set_font(self.font_main, "B", 20 if img_w else 24) # Sedikit kecilkan font jika terdesak foto
        self.pdf.set_text_color(*self.color_black)
        nama = self.data.get("full_name", "NAMA LENGKAP").upper()
        self.pdf.cell(text_width, 10, nama, align=self.header_align, ln=True)
        
        # Info Kontak
        self.pdf.set_font(self.font_main, "", 10)
        self.pdf.set_text_color(*self.color_gray)
        info = [self.data.get(k) for k in ["email", "phone", "linkedin"] if self.data.get(k)]
        
        if self.header_align == "L":
            for item in info:
                self.pdf.cell(text_width, 5, item, align="L", ln=True)
        else:
            self.pdf.cell(text_width, 6, "  |  ".join(info), align="C", ln=True)
        
        # Cek kursor Y. Jika kita menggunakan foto, pastikan teks di bawahnya tidak menabrak!
        current_y = self.pdf.get_y()
        min_y = 15 + (45 if photo_ratio == "2x3" else 40) + 5
        if img_w and current_y < min_y:
            self.pdf.set_y(min_y)
        else:
            self.pdf.ln(5)

    def _render_section_title(self, title):
        self.pdf.ln(3)
        self.pdf.set_font(self.font_main, "B", 11)
        self.pdf.set_text_color(*self.color_accent if title == "RINGKASAN PROFESIONAL" else self.color_black)
        self.pdf.cell(0, 8, title, ln=True)
        
        if self.show_line:
            x, y = self.pdf.get_x(), self.pdf.get_y()
            self.pdf.set_draw_color(*self.color_accent)
            self.pdf.line(x, y, x + 180, y)
            self.pdf.ln(2)

    def _render_summary(self):
        self.pdf.set_font(self.font_main, "", 10)
        self.pdf.set_text_color(*self.color_gray)
        self.pdf.multi_cell(0, 5, self.data.get("summary", ""))

    def _render_education(self):
        for edu in self.data.get("education", []):
            self.pdf.set_font(self.font_main, "B", 10)
            self.pdf.set_text_color(*self.color_black)
            self.pdf.cell(140, 6, edu.get("institution", ""), ln=0)
            self.pdf.set_font(self.font_main, "", 10)
            self.pdf.cell(40, 6, edu.get("year", ""), align="R", ln=1)
            
            self.pdf.set_font(self.font_main, "I", 10)
            self.pdf.set_text_color(*self.color_gray)
            gpa = f" (IPK: {edu.get('gpa')})" if edu.get("gpa") else ""
            self.pdf.cell(0, 5, f"{edu.get('degree', '')}{gpa}", ln=1)
            self.pdf.ln(1)

    def _render_experience(self):
        for exp in self.data.get("experience", []):
            self.pdf.set_font(self.font_main, "B", 10)
            self.pdf.set_text_color(*self.color_black)
            self.pdf.cell(130, 6, exp.get("role", ""), ln=0)
            self.pdf.set_font(self.font_main, "", 10)
            tgl = f"{exp.get('start_date')} - {exp.get('end_date')}"
            self.pdf.cell(50, 6, tgl, align="R", ln=1)
            
            self.pdf.set_font(self.font_main, "I", 10)
            self.pdf.set_text_color(*self.color_gray)
            self.pdf.cell(0, 5, exp.get("company", ""), ln=1)
            
            self.pdf.set_font(self.font_main, "", 10)
            for point in exp.get("description", []):
                self.pdf.multi_cell(0, 5, f"- {point}")
            self.pdf.ln(2)

    def _render_organization(self):
        for org in self.data.get("organizations", []):
            self.pdf.set_font(self.font_main, "B", 10)
            self.pdf.set_text_color(*self.color_black)
            self.pdf.cell(130, 6, org.get("role", ""), ln=0)
            self.pdf.set_font(self.font_main, "", 10)
            tgl = f"{org.get('start_date')} - {org.get('end_date')}"
            self.pdf.cell(50, 6, tgl, align="R", ln=1)
            
            self.pdf.set_font(self.font_main, "I", 10)
            self.pdf.set_text_color(*self.color_gray)
            self.pdf.cell(0, 5, org.get("organization", ""), ln=1)
            
            self.pdf.set_font(self.font_main, "", 10)
            for point in org.get("description", []):
                self.pdf.multi_cell(0, 5, f"- {point}")
            self.pdf.ln(2)

    def _render_certification(self):
        for cert in self.data.get("certifications", []):
            self.pdf.set_font(self.font_main, "B", 10)
            self.pdf.set_text_color(*self.color_black)
            self.pdf.cell(140, 6, cert.get("name", ""), ln=0)
            self.pdf.set_font(self.font_main, "", 10)
            self.pdf.cell(40, 6, cert.get("year", ""), align="R", ln=1)
            
            self.pdf.set_font(self.font_main, "I", 10)
            self.pdf.set_text_color(*self.color_gray)
            self.pdf.cell(0, 5, f"Penerbit: {cert.get('issuer', '')}", ln=1)
            
            if cert.get("description"):
                self.pdf.set_font(self.font_main, "", 10)
                self.pdf.multi_cell(0, 5, cert.get("description", ""))
                
            self.pdf.ln(1)

    def _render_skills(self):
        self.pdf.set_font(self.font_main, "", 10)
        self.pdf.set_text_color(*self.color_gray)
        skills_text = ", ".join(self.data.get("skills", []))
        self.pdf.multi_cell(0, 5, skills_text)

    def _render_languages(self):
        self.pdf.set_font(self.font_main, "", 10)
        self.pdf.set_text_color(*self.color_gray)
        lang_text = ", ".join(self.data.get("languages", []))
        self.pdf.multi_cell(0, 5, lang_text)