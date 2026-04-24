from CRUD.Shared import muat_data, simpan_data, cetak_header, cetak_kartu_job, tampilkan_daftar_singkat

def hapus_data() -> None:
    cetak_header("HAPUS DATA PEKERJAAN")
    data = muat_data()

    if not data:
        print("\n  [INFO] Belum ada data untuk dihapus.")
        return

    print("\n  Daftar lowongan yang tersedia:")
    tampilkan_daftar_singkat(data)

    print()
    target_id = input("  Masukkan ID pekerjaan yang ingin dihapus: ").strip()
    if not target_id:
        print("  [!] ID tidak boleh kosong.")
        return

    job_ditemukan = None
    data_baru = []
    for job in data:
        if job.get("id", "").strip() == target_id:
            job_ditemukan = job
        else:
            data_baru.append(job)

    if job_ditemukan is None:
        print(f"\n  [!] Data dengan ID '{target_id}' tidak ditemukan.")
        return

    print(f"\n  Data yang akan dihapus:")
    cetak_kartu_job(job_ditemukan)
    konfirmasi = input("\n  Yakin ingin menghapus data ini? (y/n): ").strip().lower()

    if konfirmasi == "y":
        simpan_data(data_baru)
        print(f"\n  Sukses! Data '{job_ditemukan.get('Judul_Pekerjaan')}'"
              f" @ {job_ditemukan.get('Nama_Perusahaan')} berhasil dihapus.")
        print(f"     Sisa data: {len(data_baru)} lowongan.")
    else:
        print("\n  [INFO] Penghapusan dibatalkan.")

if __name__ == "__main__":
    hapus_data()
