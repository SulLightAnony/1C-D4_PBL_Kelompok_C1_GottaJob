import os
from Shared import GARIS_TEBAL, clear_menu
from Create import tambah_data
from Read import lihat_semua_data
from Update import perbarui_data
from Delete import hapus_data

def tampilkan_menu() -> None:
    print(f"\n{GARIS_TEBAL}")
    print(" DATA LOWONGAN PEKERJAAN")
    print(GARIS_TEBAL)
    print("  [1]  Tambah Data Pekerjaan Baru     (Create)")
    print("  [2]  Lihat Semua Data Pekerjaan     (Read)")
    print("  [3]  Perbarui Data Pekerjaan        (Update)")
    print("  [4]  Hapus Data Pekerjaan           (Delete)")
    print("  [0]  Keluar dari Program")
    print(GARIS_TEBAL)

def main() -> None:
    while True:
        clear_menu()
        tampilkan_menu()
        pilihan = input("  Pilih menu (0-4): ").strip()

        if pilihan == "1":
            clear_menu()
            tambah_data()
        elif pilihan == "2":
            clear_menu()
            lihat_semua_data()
        elif pilihan == "3":
            clear_menu()
            perbarui_data()
        elif pilihan == "4":
            clear_menu()
            hapus_data()
        elif pilihan == "0":
            print(f"\n{GARIS_TEBAL}")
            print("  Terima kasih! Program selesai.")
            print(GARIS_TEBAL)
            break
        else:
            print("\n  [!] Pilihan tidak valid. Masukkan angka 0-4.")

        input("\n  Tekan Enter untuk kembali ke menu utama...")

if __name__ == "__main__":
    main()
