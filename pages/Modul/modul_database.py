import os
import json
import glob

def get_root_dir():
    """Mendapatkan path root proyek."""
    # Karena file ini ada di /pages/Modul/modul_database.py
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_permanen_dir():
    """Mendapatkan path folder database permanen/Job Archive."""
    root = get_root_dir()
    return os.path.join(root, "database", "Database Permanen", "Job Archive")

def set_favorit(job_data):
    """Menyimpan satu pekerjaan sebagai favorit utama di database/Database Permanen/Favorit/favorit.json."""
    root = get_root_dir()
    fav_dir = os.path.join(root, "database", "Database Permanen", "Favorit")
    if not os.path.exists(fav_dir):
        os.makedirs(fav_dir)
    
    path = os.path.join(fav_dir, "favorit.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saat menyimpan favorit: {e}")
        return False

def get_favorit():
    """Mengambil data pekerjaan yang sedang menjadi favorit dari folder permanen."""
    root = get_root_dir()
    path = os.path.join(root, "database", "Database Permanen", "Favorit", "favorit.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def simpan_ke_database_sementara(data, nama_file):
    """
    Menyimpan data (list dictionary) ke folder database/Database Sementara.
    Nama file akan otomatis ditambahkan prefix 'temp_'.
    """
    root = get_root_dir()
    db_dir = os.path.join(root, "database", "Database Sementara")
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Tambahkan prefix temp_ jika belum ada
    if not nama_file.startswith("temp_"):
        nama_file = "temp_" + nama_file

    if not nama_file.lower().endswith(".json"):
        nama_file += ".json"
        
    full_path = os.path.join(db_dir, nama_file)
    
    existing_data = []
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"Error membaca database sementara lama: {e}")
            existing_data = []
            
    # Hindari duplikat berdasarkan Link_Lowongan
    seen_links = {item.get("Link_Lowongan") for item in existing_data if item.get("Link_Lowongan") and item.get("Link_Lowongan") != "-"}
    for item in data:
        link = item.get("Link_Lowongan", "-")
        if link == "-" or link not in seen_links:
            existing_data.append(item)
            if link != "-":
                seen_links.add(link)
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        return full_path
    except Exception as e:
        print(f"Error saat menyimpan ke database sementara: {e}")
        return None

def bersihkan_database_sementara():
    """
    Menghapus seluruh file JSON di folder 'Database Sementara'.
    """
    root = get_root_dir()
    db_dir = os.path.join(root, "database", "Database Sementara")
    
    if os.path.exists(db_dir):
        files = glob.glob(os.path.join(db_dir, "*.json"))
        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                print(f"Gagal menghapus file sementara {f}: {e}")

def simpan_ke_database_permanen(job_data, source_filename):
    """
    Menyimpan data lowongan ke file koleksi permanen di folder 'Database Permanen'.
    Data akan ditambahkan (append) ke file yang sudah ada jika filenya sudah ada.
    """
    root = get_root_dir()
    db_dir = get_database_permanen_dir()
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Bersihkan nama file (buang prefix temp_ jika ada)
    base_name = os.path.basename(source_filename)
    if base_name.startswith("temp_"):
        base_name = base_name[5:] # Buang 'temp_'
    
    full_path = os.path.join(db_dir, base_name)
    
    # Baca data lama jika ada
    existing_data = []
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except:
            existing_data = []

    # Cek duplikat berdasarkan link agar tidak menyimpan lowongan yang sama berkali-kali
    new_link = job_data.get("Link_Lowongan", "")
    is_duplicate = any(item.get("Link_Lowongan") == new_link for item in existing_data)
    
    if not is_duplicate:
        existing_data.append(job_data)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            return full_path
        except Exception as e:
            print(f"Error saat menyimpan ke database permanen: {e}")
            return None
    else:
        return "DUPLICATE"

def pindahkan_ke_database_permanen(nama_file):
    """
    (Opsional/Fungsi tambahan) Memindahkan data dari sementara ke permanen.
    """
    root = get_root_dir()
    src = os.path.join(root, "database", "Database Sementara", nama_file)
    dst = os.path.join(root, "database", "Database Permanen", nama_file)
    
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst)
        return dst
    return None
