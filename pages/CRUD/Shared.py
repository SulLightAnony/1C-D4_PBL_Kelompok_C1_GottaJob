import json
import os
import glob
import datetime
import threading

_SIMPAN_LOCK = threading.Lock()

# ─────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────
# Root project = 2 level di atas file ini (pages/CRUD/Shared.py → root)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOB_ARCHIVE_DIR = os.path.join(_ROOT, "database", "Database Permanen", "Job Archive")
JOB_POSTING_FILE = os.path.join(_ROOT, "database", "Database Permanen", "Job Posting", "Data_Upload_Job.JSON")

FIELDS = [
    ("Judul_Pekerjaan",         "Judul Pekerjaan         "),
    ("Jenis_Pekerjaan",         "Jenis Pekerjaan          (contoh: Full-time, Part-time, Freelance)"),
    ("Nama_Perusahaan",         "Nama Perusahaan          "),
    ("Lokasi",                  "Lokasi                   (contoh: Jakarta, Remote)"),
    ("Rentang_Gaji",            "Rentang Gaji             (contoh: Rp 5.000.000 - Rp 8.000.000)"),
    ("Skills",                  "Skills yang Dibutuhkan   (contoh: Python, SQL, Excel)"),
    ("Benefit_Pekerjaan",       "Benefit Pekerjaan        (contoh: BPJS, THR, Asuransi)"),
    ("Kualifikasi_Persyaratan", "Kualifikasi/Persyaratan  (contoh: S1 Informatika, min. 2 tahun)"),
    ("Deskripsi_Pekerjaan",     "Deskripsi Pekerjaan      "),
    ("Link_Lowongan",           "Link Lowongan            (contoh: https://...)"),
]

def _get_category_file(judul: str) -> str:
    """Fungsi helper untuk menentukan nama file kategori di Job Archive berdasarkan judul."""
    j = judul.lower()
    if "web" in j: return "web_developer.json"
    if "mobile" in j or "android" in j or "ios" in j: return "mobile_developer.json"
    if "game" in j: return "game_developer.json"
    if "python" in j: return "python_developer.json"
    if "penetration" in j or "pentest" in j or "security" in j or "cyber" in j: return "penetration_tester.json"
    return None # Tidak ada kategori khusus

# ─────────────────────────────────────────────
# UTILITAS FILE
# ─────────────────────────────────────────────
def muat_data() -> list:
    """Membaca data dari seluruh file di Job Archive (rekursif) yang memiliki penanda source='job_posting'."""
    if not os.path.exists(JOB_ARCHIVE_DIR):
        os.makedirs(JOB_ARCHIVE_DIR)
        
    hasil = []
    # 1. Baca dari Job Archive secara rekursif
    for root, dirs, files in os.walk(JOB_ARCHIVE_DIR):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for job in data:
                                if job.get("source") == "job_posting":
                                    hasil.append(job)
                except Exception: pass

    # 2. Baca dari Data_Upload_Job.JSON (Backup/Legacy)
    if os.path.exists(JOB_POSTING_FILE):
        try:
            with open(JOB_POSTING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for job in data:
                        job["source"] = "job_posting"
                        hasil.append(job)
        except Exception: pass
        
    return hasil

def simpan_data(data: list) -> None:
    """Menyimpan data job posting ke dalam folder kategori di Job Archive dengan pengecekan kemiripan file."""
    # 1. Kumpulkan semua data non-posting dari seluruh file .json di Job Archive (rekursif)
    files_to_update = {} # path -> list of non-posting jobs
    if not os.path.exists(JOB_ARCHIVE_DIR):
        os.makedirs(JOB_ARCHIVE_DIR)

    for root, dirs, files in os.walk(JOB_ARCHIVE_DIR):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        isi = json.load(f)
                        if isinstance(isi, list):
                            isi_bersih = [job for job in isi if job.get("source") != "job_posting"]
                            files_to_update[path] = isi_bersih
                except Exception:
                    pass

    def slugify(text: str) -> str:
        """Mengubah teks menjadi nama file yang aman."""
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
        return text

    def find_similar_in_folder(judul: str, folder_path: str) -> str:
        """Mencari file .json di folder tertentu yang namanya mirip dengan judul."""
        if not os.path.exists(folder_path):
            return None
        
        j_slug = slugify(judul)
        j_words = set(j_slug.split('_'))
        
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                f_name = file.lower().replace(".json", "")
                f_words = set(f_name.split('_'))
                
                # Cek apakah ada kata yang cocok (minimal 1 kata panjang > 3)
                overlap = j_words.intersection(f_words)
                if any(len(w) > 3 for w in overlap):
                    return os.path.join(folder_path, file)
                
                # Cek sebaliknya: apakah slug judul ada dalam nama file atau sebaliknya
                if j_slug in f_name or f_name in j_slug:
                    return os.path.join(folder_path, file)
        return None

    # 2. Distribusikan data baru
    for job in data:
        job["source"] = "job_posting"
        judul = job.get("Judul_Pekerjaan", "")
        kat = job.get("Kategori", "").strip() or "Lainnya"
        
        # Tentukan folder kategori
        kat_dir = os.path.join(JOB_ARCHIVE_DIR, kat)
        if not os.path.exists(kat_dir):
            os.makedirs(kat_dir)
            
        # Cari file yang mirip DI DALAM folder kategori tersebut
        target_path = find_similar_in_folder(judul, kat_dir)
        
        if not target_path:
            # Jika tidak ada yang mirip, buat file baru berdasarkan judul
            fname = slugify(judul) or "lowongan_baru"
            target_path = os.path.join(kat_dir, f"{fname}.json")
            
        if target_path not in files_to_update:
            files_to_update[target_path] = []
            
        files_to_update[target_path].append(job)

    # 3. Tulis ulang semua file yang terpengaruh
    with _SIMPAN_LOCK:
        for path, isi in files_to_update.items():
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(isi, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Gagal menyimpan ke {path}: {e}")

    # 4. Bersihkan Data_Upload_Job.JSON (karena data sudah pindah ke Archive)
    try:
        if os.path.exists(JOB_POSTING_FILE):
            with open(JOB_POSTING_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
    except Exception:
        pass

# ─────────────────────────────────────────────
# UTILITAS TAMPILAN
# ─────────────────────────────────────────────
GARIS_TEBAL = "=" * 65
GARIS_TIPIS = "-" * 65

def cetak_header(judul: str) -> None:
    print(f"\n{GARIS_TEBAL}")
    print(f"  {judul.upper()}")
    print(GARIS_TEBAL)

def cetak_kartu_job(job: dict, nomor: int = None) -> None:
    """Menampilkan satu data pekerjaan dalam format kartu teks."""
    prefix = f"[{nomor}] " if nomor is not None else ""
    print(f"\n{GARIS_TIPIS}")
    print(f"  {prefix}ID : {job.get('id', '-')}")
    print(GARIS_TIPIS)
    for key, label in FIELDS:
        nilai = job.get(key, "-")
        nama_field = label.split("(")[0].strip()
        print(f"  {nama_field:<30}: {nilai}")
    print(GARIS_TIPIS)

def tampilkan_daftar_singkat(data: list) -> None:
    """Menampilkan daftar ringkas (nomor, id, judul, perusahaan)."""
    if not data:
        print("\n  [INFO] Belum ada data pekerjaan.")
        return
    print(f"\n  {'No':<4} {'ID':<38} {'Judul Pekerjaan':<25} Perusahaan")
    print(f"  {'-'*4} {'-'*38} {'-'*25} {'-'*20}")
    for i, job in enumerate(data, start=1):
        job_id = job.get("id", "-")
        judul  = job.get("Judul_Pekerjaan", "-")[:24]
        kantor = job.get("Nama_Perusahaan", "-")[:19]
        print(f"  {i:<4} {job_id:<38} {judul:<25} {kantor}")

def clear_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

# ─────────────────────────────────────────────
# AUTO-DELETE: Hapus data yang sudah kadaluarsa
# ─────────────────────────────────────────────
def bersihkan_data_kadaluarsa() -> int:
    """Membaca semua data job posting, menghapus yang Tanggal_Kadaluarsa-nya sudah lewat."""
    data = muat_data()
    if not data:
        return 0

    hari_ini = datetime.date.today()
    data_valid = []
    jumlah_hapus = 0

    for job in data:
        tgl_str = job.get("Tanggal_Kadaluarsa", "").strip()
        try:
            tgl = datetime.datetime.strptime(tgl_str, "%d/%m/%Y").date()
            if tgl < hari_ini:
                jumlah_hapus += 1
                print(f"  [AUTO-DELETE] '{job.get('Judul_Pekerjaan', '-')}' "
                      f"@ {job.get('Nama_Perusahaan', '-')} "
                      f"(kadaluarsa: {tgl_str})")
            else:
                data_valid.append(job)
        except (ValueError, TypeError):
            data_valid.append(job)

    if jumlah_hapus > 0:
        simpan_data(data_valid)

    return jumlah_hapus

