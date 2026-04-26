import json
import time
import random
import os
import re
from collections import Counter
from scraper_glints import GlintsScraper

# Path absolut ke folder database/ di root project (2 level di atas pages/Scraper/)
ROOT_DIR  = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DB_DIR    = os.path.join(ROOT_DIR, "database")


def ambil_nama_dominan(daftar_judul, fallback="hasil_scraping_glints"):
    """
    Tentukan frasa paling dominan dari kumpulan judul pekerjaan.
    Cara kerja:
      1. Normalisasi setiap judul: huruf kecil, buang tanda baca.
      2. Hitung frekuensi bigram (2 kata) dan unigram (1 kata) secara TERPISAH.
      3. PRIORITASKAN bigram terlebih dahulu — unigram hanya dipakai
         jika tidak ada bigram sama sekali.
      Alasan: unigram seperti "developer" muncul di semua judul (Mobile Developer,
      Flutter Developer, dll.) sehingga frekuensinya selalu lebih tinggi dari bigram
      jika digabung, padahal bigram jauh lebih deskriptif.
    """
    STOPWORDS = {
        "dan", "atau", "di", "untuk", "dengan", "yang", "the", "and", "or",
        "for", "in", "at", "of", "to", "a", "an", "is", "on", "as",
        "staff", "staf", "posisi", "position"
    }

    if not daftar_judul:
        return fallback

    counter_bigram  = Counter()
    counter_unigram = Counter()

    for judul in daftar_judul:
        if not judul or judul == "-":
            continue
        bersih = re.sub(r"[^a-z0-9 ]", " ", judul.lower())
        kata = [w for w in bersih.split() if w and w not in STOPWORDS]

        for w in kata:
            counter_unigram[w] += 1

        for i in range(len(kata) - 1):
            counter_bigram[kata[i] + " " + kata[i + 1]] += 1

    # Gunakan bigram terbaik jika ada; fallback ke unigram jika tidak ada bigram
    if counter_bigram:
        nama_terpilih = counter_bigram.most_common(1)[0][0]
    elif counter_unigram:
        nama_terpilih = counter_unigram.most_common(1)[0][0]
    else:
        return fallback

    return nama_terpilih.replace(" ", "_")


def filter_relevan(daftar_job, keyword):
    """
    Filter daftar job agar hanya job yang judulnya relevan dengan keyword yang lolos.

    Logika: Semua kata dari keyword harus muncul di Judul_Pekerjaan (case-insensitive).
    Contoh: keyword="Game Developer"
      ✅ "Game Developer"         → ada "game" dan "developer"
      ✅ "Senior Game Developer"  → ada "game" dan "developer"
      ❌ "Flutter Developer"      → tidak ada "game"
      ❌ "Fullstack Developer"    → tidak ada "game"

    Jika keyword hanya 1 kata, cukup kata itu saja yang harus ada di judul.
    """
    kata_kunci = [w.lower() for w in keyword.split() if w.strip()]
    hasil = []
    dibuang = []
    for job in daftar_job:
        judul = job.get("Judul_Pekerjaan", "-").lower()
        if all(k in judul for k in kata_kunci):
            hasil.append(job)
        else:
            dibuang.append(job.get("Judul_Pekerjaan", "-"))
    if dibuang:
        print(f"  ⚠️  [{len(dibuang)} job tidak relevan dibuang]: {', '.join(dibuang[:5])}{'...' if len(dibuang) > 5 else ''}")
    return hasil, len(dibuang)


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

    # Nama file akan ditentukan setelah scraping selesai (berdasarkan judul dominan)
    # Sementara gunakan placeholder; nama akhir ditetapkan di bawah.
    nama_file_default = os.path.join(DB_DIR, "hasil_scraping_glints.json")
    nama_file = nama_file_default  # akan diperbarui setelah data terkumpul
    os.makedirs(DB_DIR, exist_ok=True)

    # Untuk mencegah duplikasi data jika menggunakan banyak keyword
    global_seen_links = set()
    total_duplikat_dihindari = 0
    total_tidak_relevan = 0
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

            # Filter: hanya simpan job yang judulnya mengandung semua kata dari keyword
            hasil_relevan, jml_tidak_relevan = filter_relevan(hasil_scraping, kw)
            total_tidak_relevan += jml_tidak_relevan
            print(f"  ✅ {len(hasil_relevan)}/{len(hasil_scraping)} job lolos filter relevansi untuk keyword '{kw}'.")

            duplikat_lokal = 0
            for job in hasil_relevan:
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
            # Tentukan nama file dari judul pekerjaan yang paling dominan
            semua_judul = [job.get("Judul_Pekerjaan", "-") for job in data_bersih_unik]
            nama_dominan = ambil_nama_dominan(semua_judul)
            nama_file = os.path.join(DB_DIR, f"{nama_dominan}.json")
            print(f"\n📂 Nama file ditentukan dari judul dominan: '{nama_dominan}'")

            with open(nama_file, 'w', encoding='utf-8') as f:
                json.dump(data_bersih_unik, f, ensure_ascii=False, indent=4)
            print(f" BERHASIL! {len(data_bersih_unik)} data UNIK tersimpan ke '{nama_file}'.")
        else:
            print(f"\n Tidak ada data valid yang berhasil dikumpulkan.")

    except Exception as e:
        print(f"\nError eksekusi: {e}")

    finally:
        print("\nMenutup mesin scraper...")
        mesin_scraper.close()

    print("\n==================================================")
    print(f" SEMUA PROSES SELESAI!")
    print(f" Total Data Unik Tersimpan   : {len(data_bersih_unik)}")
    print(f" Total Tidak Relevan Dibuang : {total_tidak_relevan}")
    print(f" Total Duplikat Dihindari    : {total_duplikat_dihindari}")
    print("==================================================")