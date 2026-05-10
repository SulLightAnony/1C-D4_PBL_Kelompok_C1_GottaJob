import os
from dotenv import load_dotenv
try:
    from google import genai
except ImportError:
    genai = None

# 1. Load Environment Variables dari file .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def perbagus_teks_cv(job_data, cv_text):
    if genai is None:
        return "[Error] Library 'google-genai' belum terinstal. Jalankan: pip install google-genai"
    
    try:
        client = genai.Client(api_key=API_KEY)
        model_id = "gemini-3-flash-preview" 
        
        judul = job_data.get("Judul_Pekerjaan", "Profesional") if job_data else "Profesional"
        perusahaan = job_data.get("Nama_Perusahaan", "Perusahaan") if job_data else "Perusahaan"
        kualifikasi = job_data.get("Kualifikasi_Persyaratan", "-") if job_data else "-"
        
        # 5. PROMPT EKSTRA KETAT (Tanpa Markdown sama sekali)
        prompt = f"""
        Tindak sebagai pakar rekrutmen senior. Perbagus draf profil saya untuk melamar posisi {judul} di {perusahaan}.
        Kriteria yang dicari perusahaan: {kualifikasi}.
        
        ATURAN MUTLAK & WAJIB DIIKUTI:
        1. JANGAN mengarang atau menambah fakta fiktif.
        2. DILARANG KERAS menggunakan format Markdown seperti bintang (**teks** atau *teks*), pagar (#), atau strip (-).
        3. Tulis murni dalam paragraf Plain Text biasa (Teks mentah tanpa pemformatan).
        4. Berikan HANYA teks perbaikan, tanpa basa-basi pembuka atau penutup.
        
        Draf Asli:
        "{cv_text}"
        """
        
        response = client.models.generate_content(model=model_id, contents=prompt)
        
        if response and response.text:
            return response.text.strip()
        return "[Error] Respons AI kosong."
            
    except Exception as e:
        if "429" in str(e):
            return "[Server Sibuk] Terlalu banyak request. Tunggu beberapa saat."
        return f"[Error AI] {str(e)}"