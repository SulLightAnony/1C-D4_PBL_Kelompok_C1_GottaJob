from CRUD.Shared import muat_data, cetak_header, cetak_kartu_job

def lihat_semua_data() -> None:
    cetak_header("DAFTAR SEMUA DATA PEKERJAAN")
    data = muat_data()

    if not data:
        print("\n  [INFO] Belum ada data. Tambahkan data terlebih dahulu.")
        return

    print(f"\n  Total data: {len(data)} lowongan\n")
    for i, job in enumerate(data, start=1):
        cetak_kartu_job(job, nomor=i)
    print(f"\n  Total: {len(data)} lowongan ditampilkan.")

if __name__ == "__main__":
    lihat_semua_data()
