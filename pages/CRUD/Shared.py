import json
import os
import glob
import datetime

# ─────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────
# Root project = 2 level di atas file ini (pages/CRUD/Shared.py → root)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOB_ARCHIVE_DIR = os.path.join(_ROOT, "database", "Database Permanen", "Job Archive")

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
    return "it_programmer.json"

# ─────────────────────────────────────────────
# UTILITAS FILE
# ─────────────────────────────────────────────
def muat_data() -> list:
    """Membaca data dari seluruh file di Job Archive yang memiliki penanda source='job_posting'."""
    if not os.path.exists(JOB_ARCHIVE_DIR):
        os.makedirs(JOB_ARCHIVE_DIR)
        
    hasil = []
    for file_path in glob.glob(os.path.join(JOB_ARCHIVE_DIR, "*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for job in data:
                        # Hanya memuat data yang berasal dari Job Posting
                        if job.get("source") == "job_posting":
                            hasil.append(job)
        except Exception:
            pass
    return hasil

def simpan_data(data: list) -> None:
    """Menyimpan data job posting ke dalam file-file di Job Archive dengan penanda source='job_posting'."""
    if not os.path.exists(JOB_ARCHIVE_DIR):
        os.makedirs(JOB_ARCHIVE_DIR)

    # 1. Baca semua file di Job Archive, hapus yang source == 'job_posting'
    archive_data = {}
    for file_path in glob.glob(os.path.join(JOB_ARCHIVE_DIR, "*.json")):
        filename = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                isi = json.load(f)
                if isinstance(isi, list):
                    # Simpan hanya data yang BUKAN dari Job Posting (agar data lama tidak hilang)
                    isi_bersih = [job for job in isi if job.get("source") != "job_posting"]
                    archive_data[filename] = isi_bersih
                else:
                    archive_data[filename] = []
        except Exception:
            archive_data[filename] = []

    # 2. Masukkan data job_posting yang baru ke dalam kategori yang sesuai
    for job in data:
        job["source"] = "job_posting" # Berikan penanda
        kategori_file = _get_category_file(job.get("Judul_Pekerjaan", ""))
        if kategori_file not in archive_data:
            archive_data[kategori_file] = []
        archive_data[kategori_file].append(job)

    # 3. Tulis ulang semua file yang ada di archive_data
    for filename, isi in archive_data.items():
        file_path = os.path.join(JOB_ARCHIVE_DIR, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(isi, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Gagal menyimpan ke {filename}: {e}")

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

