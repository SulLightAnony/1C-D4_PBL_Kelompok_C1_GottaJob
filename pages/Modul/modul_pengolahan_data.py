import json
import os
from collections import Counter
import urllib.request
import urllib.error

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
        freq.update(unique_skills)

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
        job_data["matched_skills"] = [s for s in job_skills if s.lower() in user_skills_set]
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

def ambil_top_skills(file_path, limit=5):
    """
    Mengambil N skill teratas berdasarkan persentase kemunculannya.
    Mengembalikan list of tuple: [(skill_name, persentase), ...]
    """
    hasil_stats = hitung_persentase_skill(file_path)
    if not hasil_stats:
        return []

    top_skills = []
    count = 0
    # hasil_stats sudah terurut berdasarkan persentase (keys) dari yang terbesar
    for persentase in hasil_stats.keys():
        for skill_name in hasil_stats[persentase]:
            if count < limit:
                top_skills.append((skill_name, int(float(persentase))))
                count += 1
            else:
                break
        if count >= limit:
            break
            
    return top_skills
