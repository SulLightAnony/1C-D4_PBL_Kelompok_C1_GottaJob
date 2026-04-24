import json
import time
import random
import os
from scraper_glints import GlintsScraper

# Path absolut ke folder database/ di root project (2 level di atas pages/Scraper/)
ROOT_DIR  = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DB_DIR    = os.path.join(ROOT_DIR, "database")

if __name__ == "__main__":
    print("==================================================")
    print("        BOT SCRAPER GLINTS (HEADLESS MODE)        ")
    print("==================================================")

    print("\n💡 Tips: Kamu bisa memasukkan lebih dari satu keyword dengan memisahkannya pakai koma.")
    print("Contoh: python developer jakarta, data scientist indonesia, frontend bandung")
    input_mentah = input("Masukkan Keyword pekerjaan: ")

    list_keywords = [kw.strip() for kw in input_mentah.split(",") if kw.strip()]

    if not list_keywords:
        print("Error: Keyword tidak boleh kosong. Program dihentikan.")
        exit()

    nama_file = os.path.join(DB_DIR, "hasil_scraping_glints.json")
    os.makedirs(DB_DIR, exist_ok=True)

    # Untuk mencegah duplikasi data jika menggunakan banyak keyword
    global_seen_links = set()
    total_duplikat_dihindari = 0
    data_bersih_unik = []

    # Memuat data yang sudah ada di JSON lama agar data baru ditambahkan ke dalamnya
    if os.path.exists(nama_file):
        try:
            with open(nama_file, 'r', encoding='utf-8') as f:
                data_lama = json.load(f)
                if isinstance(data_lama, list):
                    for job in data_lama:
                        link = job.get("Link_Lowongan")
                        if link and link != "-":
                            global_seen_links.add(link)
                    data_bersih_unik.extend(data_lama)
                    print(f"Info: Berhasil memuat {len(data_lama)} data sebelumnya dari '{nama_file}'.")
        except json.JSONDecodeError:
            print(f"Info: File '{nama_file}' kosong atau invalid. Program akan menulis file baru.")
        except Exception as e:
            print(f"Warning: Gagal membaca '{nama_file}': {e}")

    print(f"\n==================================================")
    print(f"MEMULAI PENGUMPULAN {len(list_keywords)} KEYWORD KE DALAM: {nama_file}")
    print(f"==================================================")

    mesin_scraper = GlintsScraper()

    try:
        for idx, kw in enumerate(list_keywords):
            hasil_scraping = mesin_scraper.scrape_keyword_page_1_only(kw)

            duplikat_lokal = 0
            for job in hasil_scraping:
                link = job["Link_Lowongan"]

                if link != "-" and link in global_seen_links:
                    duplikat_lokal += 1
                    total_duplikat_dihindari += 1
                    continue

                if link != "-":
                    global_seen_links.add(link)
                data_bersih_unik.append(job)

            if duplikat_lokal > 0:
                print(f"Info: {duplikat_lokal} data redundan dibuang pada keyword '{kw}'.")

            if idx < len(list_keywords) - 1:
                waktu_jeda = random.uniform(10.0, 20.0)
                print(f"Jeda {waktu_jeda:.1f} detik sebelum keyword berikutnya...")
                time.sleep(waktu_jeda)

        if data_bersih_unik:
            with open(nama_file, 'w', encoding='utf-8') as f:
                json.dump(data_bersih_unik, f, ensure_ascii=False, indent=4)
            print(f"\n BERHASIL! {len(data_bersih_unik)} data UNIK tersimpan ke '{nama_file}'.")
        else:
            print(f"\n Tidak ada data valid yang berhasil dikumpulkan.")

    except Exception as e:
        print(f"\nError eksekusi: {e}")

    finally:
        print("\nMenutup mesin scraper...")
        mesin_scraper.close()

    print("\n==================================================")
    print(f" SEMUA PROSES SELESAI!")
    print(f" Total Data Unik Tersimpan: {len(data_bersih_unik)}")
    print(f" Total Data Duplikat Dihindari: {total_duplikat_dihindari}")
    print("==================================================")