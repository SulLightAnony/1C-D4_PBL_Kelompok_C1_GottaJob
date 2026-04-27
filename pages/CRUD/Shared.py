import json
import os
import uuid
import datetime

# ─────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────
# Root project = 2 level di atas file ini (pages/CRUD/Shared.py → root)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE_NAME = os.path.join(_ROOT, "database", "Database Permanen", "Job Posting", "Data_Upload_Job.JSON")

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

# ─────────────────────────────────────────────
# UTILITAS FILE
# ─────────────────────────────────────────────
def muat_data() -> list:
    """Membaca data dari file JSON. Jika file belum ada, kembalikan list kosong."""
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            isi = f.read().strip()
            if not isi:
                return []
            data = json.loads(isi)
            if not isinstance(data, list):
                print(f"[PERINGATAN] Format file {FILE_NAME} tidak valid. Mereset data...")
                return []
            return data
    except json.JSONDecodeError:
        print(f"[PERINGATAN] File {FILE_NAME} rusak/tidak bisa dibaca. Mereset data...")
        return []

def simpan_data(data: list) -> None:
    """Menulis seluruh data ke file JSON dengan indentasi rapi."""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    """Membaca semua data, menghapus yang Tanggal_Kadaluarsa-nya sudah lewat,
    menyimpan kembali, dan mengembalikan jumlah data yang dihapus."""
    data = muat_data()
    if not data:
        return 0

    hari_ini = datetime.date.today()
    data_valid = []
    jumlah_hapus = 0

    for job in data:
        tgl_str = job.get("Tanggal_Kadaluarsa", "").strip()
        try:
            # Format yang dipakai Create.py: DD/MM/YYYY
            tgl = datetime.datetime.strptime(tgl_str, "%d/%m/%Y").date()
            if tgl < hari_ini:
                jumlah_hapus += 1
                print(f"  [AUTO-DELETE] '{job.get('Judul_Pekerjaan', '-')}' "
                      f"@ {job.get('Nama_Perusahaan', '-')} "
                      f"(kadaluarsa: {tgl_str})")
            else:
                data_valid.append(job)
        except (ValueError, TypeError):
            # Jika format tanggal tidak bisa diparse, simpan datanya
            data_valid.append(job)

    if jumlah_hapus > 0:
        simpan_data(data_valid)

    return jumlah_hapus
