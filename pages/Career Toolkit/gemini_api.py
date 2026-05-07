from google import genai

# API Key Anda
API_KEY = "AIzaSyD2axxtgG1EB4mhmBft8sRWitdDpqTlzPY"

# Inisialisasi client baru (SDK google-genai)
client = genai.Client(api_key=API_KEY)

def perbagus_teks_cv(job_data, cv_text):
    """
    Menggunakan Gemini 2.0 Flash untuk memoles teks CV berdasarkan target lowongan.
    """
    try:
        # Update ke model terbaru 2026: gemini-2.0-flash
        model_id = "gemini-3-flash-preview" 
        
        # Ekstrak data konteks
        judul = job_data.get("Judul_Pekerjaan", "profesional") if job_data else "profesional"
        perusahaan = job_data.get("Nama_Perusahaan", "perusahaan target") if job_data else "perusahaan target"
        kualifikasi = job_data.get("Kualifikasi_Persyaratan", "-") if job_data else "-"
        
        prompt = f"""
        Tindak sebagai pakar rekrutmen profesional. 
        Saya sedang menyusun CV untuk posisi {judul} di {perusahaan}.
        Persyaratan mereka: {kualifikasi}.
        
        Tugas: Perbagus teks CV saya agar lebih profesional, menggunakan kata kerja aksi, 
        dan ramah ATS (sesuaikan dengan persyaratan di atas).
        
        ATURAN:
        1. JANGAN mengarang data atau pengalaman baru.
        2. Berikan HANYA teks hasil perbaikannya saja.
        3. Gunakan format plain text (JANGAN gunakan markdown seperti **bold**).
        
        Teks Asli:
        "{cv_text}"
        """
        
        # Cara panggil baru di SDK google-genai
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        return f"[ERROR AI] Gagal memproses: {str(e)}"