import uuid
import datetime
import calendar
from CRUD.Shared import muat_data, simpan_data, cetak_header, FIELDS

NAMA_BULAN = {
    1:"Januari", 2:"Februari", 3:"Maret",    4:"April",
    5:"Mei",     6:"Juni",     7:"Juli",      8:"Agustus",
    9:"September",10:"Oktober",11:"November",12:"Desember"
}

# ─────────────────────────────────────────────
# HELPER: Input tanggal kadaluarsa dengan validasi
# ─────────────────────────────────────────────
def _input_tanggal_kadaluarsa() -> str:
    """Meminta user memasukkan tanggal kadaluarsa: Hari → Bulan → Tahun.
    Validasi dilakukan setelah ketiga nilai diisi."""

    print("\n  ── Tanggal Kadaluarsa Lowongan ──")
    hari_ini = datetime.date.today()
    tahun_sekarang = hari_ini.year

    while True:
        # --- Hari ---
        try:
            hari = int(input("  Hari   (1–31) : ").strip())
            if not (1 <= hari <= 31):
                print("  [!] Hari harus antara 1 – 31.")
                continue
        except ValueError:
            print("  [!] Masukkan angka yang valid untuk hari.")
            continue

        # --- Bulan ---
        try:
            bulan = int(input("  Bulan  (1–12) : ").strip())
            if not (1 <= bulan <= 12):
                print("  [!] Bulan harus antara 1 – 12.")
                continue
        except ValueError:
            print("  [!] Masukkan angka yang valid untuk bulan.")
            continue

        # --- Tahun ---
        try:
            tahun = int(input(f"  Tahun  (contoh: {tahun_sekarang}) : ").strip())
            if not (tahun_sekarang <= tahun <= tahun_sekarang + 10):
                print(f"  [!] Tahun harus antara {tahun_sekarang} – {tahun_sekarang + 10}.")
                continue
        except ValueError:
            print("  [!] Masukkan angka yang valid untuk tahun.")
            continue

        # --- Validasi gabungan ---
        max_hari = calendar.monthrange(tahun, bulan)[1]
        if hari > max_hari:
            print(f"  [!] Bulan {NAMA_BULAN[bulan]} {tahun} hanya punya {max_hari} hari. Silakan ulangi.")
            continue

        tgl = datetime.date(tahun, bulan, hari)
        if tgl < hari_ini:
            print(f"  [!] Tanggal kadaluarsa tidak boleh di masa lalu (hari ini: {hari_ini.strftime('%d/%m/%Y')}). Silakan ulangi.")
            continue

        break

    tanggal_str = f"{hari:02d}/{bulan:02d}/{tahun}"
    print(f"  ✓ Kadaluarsa: {hari} {NAMA_BULAN[bulan]} {tahun}")
    return tanggal_str



# ─────────────────────────────────────────────
# FUNGSI UTAMA
# ─────────────────────────────────────────────
def tambah_data() -> None:
    cetak_header("TAMBAH DATA PEKERJAAN BARU")
    print("  Isi setiap field berikut (tekan Enter untuk melanjutkan).\n")

    job_baru = {"id": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    # === Input Field-Field Lainnya ===
    for key, label in FIELDS:
        nama_tampil = label.split("(")[0].strip()
        hint = ""
        if "(" in label:
            hint = "  » " + label[label.index("("):]
        while True:
            if hint:
                print(f"  {nama_tampil}")
                print(f"{hint}")
                nilai = input("  Jawaban : ").strip()
            else:
                nilai = input(f"  {nama_tampil}: ").strip()
            if nilai:
                job_baru[key] = nilai
                break
            else:
                print("  [!] Field ini wajib diisi. Silakan coba lagi.")

    # === Input Tanggal Kadaluarsa (di akhir) ===
    job_baru["Tanggal_Kadaluarsa"] = _input_tanggal_kadaluarsa()
    print()

    data = muat_data()
    data.append(job_baru)
    simpan_data(data)

    print(f"\n  Sukses! Data berhasil ditambahkan.")
    print(f"     ID             : {job_baru['id']}")
    print(f"     Kadaluarsa     : {job_baru['Tanggal_Kadaluarsa']}")
    print(f"     Judul          : {job_baru['Judul_Pekerjaan']} @ {job_baru['Nama_Perusahaan']}")

if __name__ == "__main__":
    tambah_data()
