import json
import os
from collections import Counter
import urllib.request
import urllib.error
from Modul.modul_kategorisasi import pisahkan_skill

def validasi_link_pekerjaan(job_list):
    """
    Mengecek apakah link lowongan masih bisa dibuka.
    Mengembalikan list job yang link-nya masih aktif.
    """
    job_aktif = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    for job in job_list:
        url = job.get("Link_Lowongan", "")
        if not url or url == "#":
            job_aktif.append(job)
            continue
            
        try:
            # Tahap 1: Coba HEAD (lebih cepat)
            req = urllib.request.Request(url, headers=headers, method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status in [200, 301, 302]:
                    job_aktif.append(job)
                    continue
        except urllib.error.HTTPError as e:
            # Jika 403 atau 500, kemungkinan bot diblokir tapi link masih ada
            if e.code in [403, 500, 503]:
                job_aktif.append(job)
                continue
            # Jika 404, berarti sudah pasti mati
            if e.code in [404, 410]:
                pass # Jangan masukkan ke job_aktif
            else:
                # Coba tahap 2: GET (beberapa server menolak HEAD)
                try:
                    req_get = urllib.request.Request(url, headers=headers, method='GET')
                    with urllib.request.urlopen(req_get, timeout=5) as resp_get:
                        if resp_get.status in [200, 301, 302]:
                            job_aktif.append(job)
                except:
                    pass
        except:
            # Untuk error lain (timeout, connection), kita anggap masih aktif 
            # agar tidak menghapus data secara sembarangan jika internet tidak stabil
            job_aktif.append(job)
            
    return job_aktif


def hitung_persentase_skill(file_path):
    """
    Membaca file JSON hasil scraping, menghitung frekuensi skill,
    dan mengelompokkan skill berdasarkan persentase yang sama.
    """
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_lowongan = len(data)
    if total_lowongan == 0:
        return {}

    freq = Counter()

    for item in data:
        raw_skills = item.get("Skills", "")
        all_skills = []
        lines = raw_skills.split("\n")
        for line in lines:
            parts = line.split("|")
            for p in parts:
                cleaned = p.strip()
                if cleaned and cleaned != "-":
                    all_skills.append(cleaned)
        
        unique_skills = set(all_skills)
        # Filter: Hanya masukkan Hard Skills ke dalam hitung_persentase_skill
        categorized = pisahkan_skill(list(unique_skills))
        freq.update(categorized["hard_skills"])

    # Hitung persentase dan kelompokkan berdasarkan persentase yang sama
    # Format: { persentase: [list_skill] }
    hasil_pengelompokan = {}
    
    for skill, count in freq.items():
        persentase = round((count / total_lowongan) * 100, 1)
        
        if persentase not in hasil_pengelompokan:
            hasil_pengelompokan[persentase] = []
        
        hasil_pengelompokan[persentase].append(skill)

    # Urutkan berdasarkan persentase terbesar
    sorted_keys = sorted(hasil_pengelompokan.keys(), reverse=True)
    hasil_final = {k: hasil_pengelompokan[k] for k in sorted_keys}

    return hasil_final

def ambil_jenis_pekerjaan_unik(file_path):
    """
    Mengambil daftar jenis pekerjaan unik dari file JSON,
    dengan normalisasi casing agar tidak ada duplikat.
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    unique_types = set()
    for item in data:
        t = item.get("Jenis_Pekerjaan", "").strip()
        if t and t != "-":
            # Normalisasi ke Title Case agar 'magang' dan 'Magang' jadi satu
            unique_types.add(t.title())
            
    return sorted(list(unique_types))

def cari_pekerjaan_cocok(file_path, selected_skills, selected_job_types=None):
    """
    Mencari pekerjaan yang memiliki kecocokan skill paling tinggi 
    dengan list skill yang dipilih user dan tipe pekerjaan opsional.
    """
    if not os.path.exists(file_path) or not selected_skills:
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_skills_set = set(s.lower() for s in selected_skills)
    
    if selected_job_types:
        user_types_set = set(t.lower() for t in selected_job_types)
    else:
        user_types_set = set()

    hasil_pencarian = []

    for item in data:
        # Tentukan apakah jenis pekerjaan cocok (jika ada filter)
        is_type_match = True
        if user_types_set:
            job_type = item.get("Jenis_Pekerjaan", "").lower()
            is_type_match = any(t in job_type or job_type in t for t in user_types_set)

        raw_skills = item.get("Skills", "")
        job_skills = []
        lines = raw_skills.split("\n")
        for line in lines:
            parts = line.split("|")
            for p in parts:
                cleaned = p.strip()
                if cleaned and cleaned != "-":
                    job_skills.append(cleaned.lower())
        
        job_skills_set = set(job_skills)
        
        # Hitung irisan (skill yang cocok)
        matched_skills = user_skills_set.intersection(job_skills_set)
        
        # Persentase kecocokan: (berapa skill user yang ada di lowongan) / (total skill lowongan)
        if job_skills_set:
            persentase = (len(matched_skills) / len(job_skills_set)) * 100
        else:
            persentase = 0.0
            
        # Tambahkan data pekerjaan ke hasil pencarian
        job_data = item.copy()
        job_data["match_percentage"] = round(persentase, 1)
        
        # Kategorisasi matched skills (yang dimiliki user)
        matched_list = [s for s in job_skills if s.lower() in user_skills_set]
        job_data["matched_categorized"] = pisahkan_skill(matched_list)
        
        # Kategorisasi ALL skills (yang dibutuhkan lowongan)
        all_skills_list = [s.strip() for s in raw_skills.replace("\n", "|").split("|") if s.strip()]
        job_data["all_categorized"] = pisahkan_skill(all_skills_list)
        
        job_data["matched_skills"] = matched_list # Tetap simpan format lama untuk kompatibilitas
        job_data["is_type_match"] = is_type_match
        hasil_pencarian.append(job_data)

    # Urutkan: 1. Berdasarkan persentase skill, 2. Berdasarkan kecocokan tipe
    hasil_pencarian.sort(key=lambda x: (x["match_percentage"], x["is_type_match"]), reverse=True)
    return hasil_pencarian

def ambil_insight_pasar(file_path):
    """
    Menghasilkan teks insight pasar (skill dominan, status kontrak, dan rata-rata gaji)
    berdasarkan data dalam file JSON.
    """
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_jobs = json.load(f)
        
        if not all_jobs:
            return None

        # 1. Insight Skill
        teks_insight = "Belum ada tren skill yang terdeteksi."
        hasil_stats = hitung_persentase_skill(file_path)
        if hasil_stats:
            persentase_top = list(hasil_stats.keys())[0]
            skill_top = " & ".join(hasil_stats[persentase_top][:2])
            teks_insight = f"Pelajari {skill_top}."

        # 2. Insight Kontrak
        teks_kontrak = "Data status pekerjaan belum tersedia."
        status_list = [j.get("Jenis_Pekerjaan", "Full-time") for j in all_jobs]
        most_common_status_list = Counter(status_list).most_common(1)
        if most_common_status_list:
            most_common_status = most_common_status_list[0][0]
            teks_kontrak = f"Mayoritas posisi berstatus {most_common_status}."

        # 3. Insight Gaji
        teks_gaji = "Informasi gaji belum tersedia."
        import re
        gaji_list = []
        for j in all_jobs:
            gaji_str = j.get("Rentang_Gaji", "")
            # Bersihkan titik dan ambil angka
            angka = re.findall(r'\d+', gaji_str.replace('.', ''))
            if angka:
                rata_rata_job = sum(map(int, angka)) / len(angka)
                gaji_list.append(rata_rata_job)
        
        if gaji_list:
            avg_gaji = sum(gaji_list) / len(gaji_list)
            teks_gaji = f"Gaji rata-rata sekitar Rp {avg_gaji/1_000_000:.1f} jt/bulan."

        return {
            "skill": teks_insight,
            "kontrak": teks_kontrak,
            "gaji": teks_gaji
        }
    except Exception as e:
        print(f"Error ambil_insight_pasar: {e}")
        return None



def ambil_top_skills_count(file_path, limit=5):
    """
    Mengambil N skill teratas berdasarkan JUMLAH kemunculannya (bukan persentase).
    Mengembalikan list of tuple: [(skill_name, count), ...]
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        return []

    freq = Counter()

    for item in data:
        raw_skills = item.get("Skills", "")
        all_skills = []
        lines = raw_skills.split("\n")
        for line in lines:
            parts = line.split("|")
            for p in parts:
                cleaned = p.strip()
                if cleaned and cleaned != "-":
                    all_skills.append(cleaned)
        
        unique_skills = set(all_skills)
        categorized = pisahkan_skill(list(unique_skills))
        freq.update(categorized["hard_skills"])

    # Ambil limit teratas berdasarkan jumlah terbanyak
    top_common = freq.most_common(limit)
    return top_common

def hitung_gap_skill(job_data):
    """
    Menghitung skill yang belum dikuasai berdasarkan data pekerjaan favorit.
    Mengembalikan list skill yang perlu dipelajari.
    """
    if not job_data:
        return []
        
    # Ambil semua skill yang ada di lowongan favorit
    raw_skills = job_data.get("Skills", "")
    semua_skill = [s.strip().lower() for s in raw_skills.split("|") if s.strip() and s.strip() != "-"]

    # Ambil matched skill yang sudah dimiliki
    skill_dimiliki = [s.strip().lower() for s in job_data.get("matched_skills", [])]

    # Filter: ambil skill yang dibutuhkan tapi belum dimiliki
    gap_list = [s.title() for s in semua_skill if s not in skill_dimiliki]
    
    # Hilangkan duplikat dan urutkan
    return sorted(list(set(gap_list)))

def cari_archive_terdekat(judul_pekerjaan, folder_archive):
    """
    Mencari file JSON di folder archive yang paling cocok dengan judul pekerjaan.
    Menggunakan logika hitung kecocokan kata kunci.
    """
    import glob
    if not os.path.exists(folder_archive):
        return None
        
    # Cari secara rekursif ke dalam subfolder kategori
    semua_file = glob.glob(os.path.join(folder_archive, "**", "*.json"), recursive=True)
    keywords = [k.lower() for k in judul_pekerjaan.split() if len(k) > 2]
    
    best_match_count = 0
    archive_json = None
    
    for file_path in semua_file:
        nama_file_kecil = os.path.basename(file_path).lower()
        match_count = sum(1 for key in keywords if key in nama_file_kecil)
        
        if match_count > best_match_count:
            best_match_count = match_count
            archive_json = file_path
            
    return archive_json if best_match_count > 0 else None


def hitung_total_lowongan_aktif():
    """
    Menghitung total lowongan aktif (jumlah data/item di seluruh JSON kategori dalam database permanen).
    """
    try:
        hasil_persentase = hitung_persentase_lowongan_per_kategori()
        return sum(item["jumlah"] for item in hasil_persentase.values())
    except Exception as e:
        print(f"Error hitung_total_lowongan_aktif: {e}")
        return 0


def hitung_persentase_lowongan_per_kategori():
    """
    Menghitung jumlah lowongan per kategori dan persentasenya terhadap total lowongan aktif.
    Mengembalikan dict: { nama_kategori: (jumlah, persentase) } terurut berdasarkan jumlah terbesar.
    """
    import glob
    from Modul.modul_database import get_database_permanen_dir, KATEGORI_GLINTS
    
    try:
        db_dir = get_database_permanen_dir()
        if not os.path.exists(db_dir):
            return {}
        
        # Inisialisasi hitungan untuk setiap kategori resmi Glints
        kategori_counts = {kat: 0 for kat in KATEGORI_GLINTS}
        total_lowongan = 0
        
        # Cari seluruh file JSON di folder Job Archive secara rekursif
        file_paths = glob.glob(os.path.join(db_dir, "**", "*.json"), recursive=True)
        for fp in file_paths:
            try:
                # Dapatkan nama kategori dari nama parent folder
                parent_folder = os.path.basename(os.path.dirname(fp))
                
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        count = len(data)
                        total_lowongan += count
                        
                        # Masukkan ke kategori yang sesuai
                        if parent_folder in kategori_counts:
                            kategori_counts[parent_folder] += count
                        elif parent_folder != "Job Archive":
                            kategori_counts[parent_folder] = kategori_counts.get(parent_folder, 0) + count
                        else:
                            kategori_counts["Lainnya"] = kategori_counts.get("Lainnya", 0) + count
            except Exception as e:
                print(f"Error saat membaca file {fp} untuk per kategori: {e}")
                
        # Jika tidak ada lowongan sama sekali, hindari pembagian dengan nol
        if total_lowongan == 0:
            return {}
            
        # Hitung persentase dan buat hasil
        hasil = {}
        for kat, count in kategori_counts.items():
            if count > 0: # Hanya tampilkan kategori yang memiliki lowongan aktif
                persentase = round((count / total_lowongan) * 100)
                hasil[kat] = {
                    "jumlah": count,
                    "persentase": persentase
                }
                
        # Urutkan berdasarkan jumlah lowongan terbanyak
        sorted_hasil = dict(sorted(hasil.items(), key=lambda item: item[1]["jumlah"], reverse=True))
        return sorted_hasil
    except Exception as e:
        print(f"Error hitung_persentase_lowongan_per_kategori: {e}")
        return {}


def hitung_tren_bidang_aktif(baseline_counts):
    """
    Menghitung statistik dan trend untuk card BIDANG AKTIF pada Dashboard Admin.
    Membandingkan data saat ini dengan baseline_counts dari sesi aktif.
    Mengembalikan list of dict: [
        { "nama": "Administrasi & HRD", "jumlah": 14, "trend": "↑", "warna": "#27AE60" },
        ...
    ]
    """
    try:
        data_kategori = hitung_persentase_lowongan_per_kategori()
        
        # Jika baseline_counts kosong, inisialisasi baseline sesi dengan kondisi saat ini
        if not baseline_counts:
            for kat, info in data_kategori.items():
                baseline_counts[kat] = info["jumlah"]
        
        hasil = []
        for kat, info in data_kategori.items():
            current_val = info["jumlah"]
            # default ke 0 jika sebelumnya tidak ada data sama sekali di folder tersebut
            baseline_val = baseline_counts.get(kat, 0)
            
            # Hitung trend
            if current_val > baseline_val:
                trend = "↑"
                warna = "#27AE60" # Hijau (naik)
                trend_weight = 3
            elif current_val < baseline_val:
                trend = "↓"
                warna = "#E74C3C" # Merah (turun)
                trend_weight = 1
            else:
                trend = "-"
                warna = "#95A5A6" # Abu-abu (netral)
                trend_weight = 2
                
            hasil.append({
                "nama": kat,
                "jumlah": current_val,
                "trend": trend,
                "warna": warna,
                "weight": trend_weight
            })
            
        # Urutkan berdasarkan bobot tren (positif ↑ dulu, lalu netral -, lalu negatif ↓)
        # Jika bobot tren sama, urutkan berdasarkan jumlah lowongan terbanyak
        sorted_hasil = sorted(hasil, key=lambda x: (-x["weight"], -x["jumlah"]))
        return sorted_hasil
    except Exception as e:
        print(f"Error hitung_tren_bidang_aktif: {e}")
        return []

def ambil_skill_tidak_terklasifikasi(limit=5):
    """
    Mencari semua skill unik dari database yang memiliki tingkat kepercayaan rendah (Low Confidence)
    di NLP engine (tidak terklasifikasi secara baku).
    Mengembalikan total count (int) dan list dict top unclassified skills sorted by count.
    """
    import glob
    from Modul.modul_kategorisasi import categorizer
    
    # Dapatkan path root folder Job Archive
    modul_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(modul_dir))
    db_dir = os.path.join(root_dir, "database", "Database Permanen", "Job Archive")
    
    if not os.path.exists(db_dir):
        return 0, []
        
    file_paths = glob.glob(os.path.join(db_dir, "**", "*.json"), recursive=True)
    
    skill_counts = {} # { skill_raw: count }
    
    for fp in file_paths:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                jobs = json.load(f)
            if not isinstance(jobs, list):
                continue
            for job in jobs:
                raw_skills = job.get("Skills", "")
                if not raw_skills or raw_skills == "-":
                    continue
                parts = [s.strip() for s in raw_skills.split("|") if s.strip()]
                for s in parts:
                    s_lower = s.lower()
                    normalized = categorizer._normalize(s_lower)
                    s_baku = normalized.title()
                    skill_counts[s_baku] = skill_counts.get(s_baku, 0) + 1
        except:
            continue
            
    # Klasifikasikan setiap skill unik di memori
    unclassified_list = []
    total_unclassified_unique = 0
    
    for skill_baku, count in skill_counts.items():
        res = categorizer._klasifikasi_satu(skill_baku)
        if res and res.confidence == "low":
            total_unclassified_unique += 1
            unclassified_list.append({
                "skill": skill_baku,
                "count": count
            })
            
    # Urutkan berdasarkan kemunculan terbanyak
    unclassified_list.sort(key=lambda x: x["count"], reverse=True)
    
    return total_unclassified_unique, unclassified_list[:limit]

def cari_kategori_untuk_skill(skill_name):
    """
    Mencari bidang (nama subfolder di Job Archive) tempat skill_name pertama kali ditemukan.
    Aman dari circular imports (tidak mengimpor modul_kategorisasi).
    """
    import glob
    import json
    
    modul_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(modul_dir))
    db_dir = os.path.join(root_dir, "database", "Database Permanen", "Job Archive")
    
    if not os.path.exists(db_dir):
        return None
        
    target_lower = skill_name.strip().lower()
    
    # Ambil semua folder kategori di Job Archive
    for entry in os.scandir(db_dir):
        if entry.is_dir():
            cat_name = entry.name
            # Scan semua file json di folder ini
            for fp in glob.glob(os.path.join(entry.path, "*.json")):
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        jobs = json.load(f)
                    if not isinstance(jobs, list):
                        continue
                    for job in jobs:
                        raw_skills = job.get("Skills", "")
                        if not raw_skills:
                            continue
                        parts = [s.strip().lower() for s in raw_skills.split("|")]
                        # Cocokkan langsung atau dengan mengabaikan spasi/normalisasi sederhana
                        if target_lower in parts:
                            return cat_name
                        for s in parts:
                            if s == target_lower or s.replace(" ", "") == target_lower.replace(" ", ""):
                                return cat_name
                except:
                    continue
    return None
