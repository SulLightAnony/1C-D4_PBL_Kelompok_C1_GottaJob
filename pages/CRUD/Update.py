from Shared import muat_data, simpan_data, cetak_header, cetak_kartu_job, tampilkan_daftar_singkat, FIELDS

def perbarui_data() -> None:
    cetak_header("PERBARUI DATA PEKERJAAN")
    data = muat_data()

    if not data:
        print("\n  [INFO] Belum ada data untuk diperbarui.")
        return

    print("\n  Daftar lowongan yang tersedia:")
    tampilkan_daftar_singkat(data)

    print()
    target_id = input("  Masukkan ID pekerjaan yang ingin diperbarui: ").strip()
    if not target_id:
        print("  [!] ID tidak boleh kosong.")
        return

    index_ditemukan = None
    for i, job in enumerate(data):
        if job.get("id", "").strip() == target_id:
            index_ditemukan = i
            break

    if index_ditemukan is None:
        print(f"\n  [!] Data dengan ID '{target_id}' tidak ditemukan.")
        return

    job = data[index_ditemukan]
    print("\n  Data ditemukan:")
    cetak_kartu_job(job)

    print(f"\n  Pilih field yang ingin diperbarui:\n")
    for idx, (key, label) in enumerate(FIELDS, start=1):
        nama_tampil = label.split("(")[0].strip()
        nilai_lama  = job.get(key, "-")
        print(f"  [{idx:>2}] {nama_tampil:<30}: {nilai_lama}")
    print(f"\n  [ 0] Batal / Kembali")

    while True:
        try:
            pilihan_input = input("\n  Pilih nomor field (0 untuk batal): ").strip()
            if not pilihan_input:
                continue
            pilihan_field = int(pilihan_input)
        except ValueError:
            print("  [!] Masukkan angka yang valid.")
            continue
        if pilihan_field == 0:
            print("  [INFO] Pembaruan dibatalkan.")
            return
        if 1 <= pilihan_field <= len(FIELDS):
            break
        print(f"  [!] Pilihan harus antara 0-{len(FIELDS)}.")

    key_dipilih, label_dipilih = FIELDS[pilihan_field - 1]
    nama_tampil = label_dipilih.split("(")[0].strip()
    nilai_lama  = job.get(key_dipilih, "")

    print(f"\n  Field     : {nama_tampil}")
    print(f"  Nilai lama: {nilai_lama}")

    while True:
        nilai_baru = input("  Nilai baru: ").strip()
        if nilai_baru:
            break
        print("  [!] Nilai baru tidak boleh kosong.")

    data[index_ditemukan][key_dipilih] = nilai_baru
    simpan_data(data)

    print(f"\n  Sukses! Field '{nama_tampil}' berhasil diperbarui.")
    print(f"     Lama : {nilai_lama}")
    print(f"     Baru : {nilai_baru}")

if __name__ == "__main__":
    perbarui_data()
