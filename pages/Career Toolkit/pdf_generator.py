import os
from fpdf import FPDF

class ATS_PDF(FPDF):
    def footer(self):
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
        
        # Default Styling
        self.font_main = "helvetica"
        self.color_black = (0, 0, 0)
        self.color_gray = (60, 60, 60)
        self.color_accent = (44, 104, 123) # Biru GottaJob
        self.show_line = True

    def _apply_template_style(self, template_id):
        """Mengatur gaya visual berdasarkan ID template yang dipilih."""
        if template_id == "ats_modern":
            self.font_main = "times" # Times New Roman sangat formal
            self.color_accent = (0, 0, 0) # Hitam putih murni
            self.show_line = True
        elif template_id == "ats_minimalist":
            self.font_main = "helvetica"
            self.color_accent = (200, 200, 200) # Garis abu-abu tipis
            self.show_line = False
        else: # ats_classic
            self.font_main = "helvetica"
            self.color_accent = (44, 104, 123)
            self.show_line = True

    def generate_pdf(self, output_path, template_id="ats_classic"):
        self._apply_template_style(template_id)
        
        self._render_header()
        
        if self.data.get("summary"):
            self._render_section_title("RINGKASAN PROFESIONAL")
            self._render_summary()
            
        if self.data.get("education"):
            self._render_section_title("RIWAYAT PENDIDIKAN")
            self._render_education()

        if self.data.get("experience"):
            self._render_section_title("PENGALAMAN KERJA")
            self._render_experience()

        if self.data.get("skills"):
            self._render_section_title("KEAHLIAN & TEKNOLOGI")
            self._render_skills()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.pdf.output(output_path)
        return output_path

    def _render_header(self):
        self.pdf.set_font(self.font_main, "B", 22)
        self.pdf.set_text_color(*self.color_black)
        nama = self.data.get("full_name", "NAMA LENGKAP").upper()
        self.pdf.cell(0, 12, nama, align="C", ln=True)
        
        self.pdf.set_font(self.font_main, "", 10)
        self.pdf.set_text_color(*self.color_gray)
        
        info = [self.data.get(k) for k in ["email", "phone", "linkedin"] if self.data.get(k)]
        self.pdf.cell(0, 6, "  |  ".join(info), align="C", ln=True)
        self.pdf.ln(5)

    def _render_section_title(self, title):
        self.pdf.ln(4)
        self.pdf.set_font(self.font_main, "B", 11)
        self.pdf.set_text_color(*self.color_black)
        self.pdf.cell(0, 8, title, ln=True)
        
        if self.show_line:
            x, y = self.pdf.get_x(), self.pdf.get_y()
            self.pdf.set_draw_color(*self.color_accent)
            self.pdf.line(x, y, x + 185, y)
        self.pdf.ln(3)

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
            self.pdf.cell(45, 6, edu.get("year", ""), align="R", ln=1)
            
            self.pdf.set_font(self.font_main, "I", 10)
            self.pdf.set_text_color(*self.color_gray)
            gpa = f" (IPK: {edu.get('gpa')})" if edu.get("gpa") else ""
            self.pdf.cell(0, 5, f"{edu.get('degree', '')}{gpa}", ln=1)
            self.pdf.ln(2)

    def _render_experience(self):
        for exp in self.data.get("experience", []):
            self.pdf.set_font(self.font_main, "B", 10)
            self.pdf.set_text_color(*self.color_black)
            self.pdf.cell(140, 6, exp.get("role", ""), ln=0)
            self.pdf.set_font(self.font_main, "", 10)
            tgl = f"{exp.get('start_date')} - {exp.get('end_date')}"
            self.pdf.cell(45, 6, tgl, align="R", ln=1)
            
            self.pdf.set_font(self.font_main, "I", 10)
            self.pdf.set_text_color(*self.color_gray)
            self.pdf.cell(0, 5, exp.get("company", ""), ln=1)
            
            self.pdf.set_font(self.font_main, "", 10)
            for point in exp.get("description", []):
                self.pdf.multi_cell(0, 5, f"- {point}")
            self.pdf.ln(2)

    def _render_skills(self):
        self.pdf.set_font(self.font_main, "", 10)
        self.pdf.set_text_color(*self.color_gray)
        skills_text = ", ".join(self.data.get("skills", []))
        self.pdf.multi_cell(0, 5, skills_text)