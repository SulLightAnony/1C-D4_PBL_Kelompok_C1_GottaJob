import uuid
import datetime
from Shared import muat_data, simpan_data, cetak_header, FIELDS

def tambah_data() -> None:
    cetak_header("TAMBAH DATA PEKERJAAN BARU")
    print("  Isi setiap field berikut (tekan Enter untuk melanjutkan).\n")

    job_baru = {"id": datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")}
  
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

    data = muat_data()
    data.append(job_baru)
    simpan_data(data)

    print(f"\n  Sukses! Data berhasil ditambahkan.")
    print(f"     ID   : {job_baru['id']}")
    print(f"     Judul: {job_baru['Judul_Pekerjaan']} @ {job_baru['Nama_Perusahaan']}")

if __name__ == "__main__":
    tambah_data()
