import os
import json
import glob
import threading

# -----------------------------------------------------------------------
# Daftar resmi kategori pekerjaan dari Glints Indonesia.
# Digunakan untuk normalisasi nama folder agar konsisten.
# -----------------------------------------------------------------------
KATEGORI_GLINTS = [
    "Akuntansi",
    "Administrasi & HRD",
    "Seni, Media, & Komunikasi",
    "Konstruksi & Real Estate",
    "Business Development & Sales",
    "Komputer & Perangkat Lunak",
    "Konsultan",
    "Desain",
    "Pendidikan & Pelatihan",
    "Keuangan",
    "Perangkat Keras & Elektronik",
    "Kesehatan",
    "Hotel & Travel",
    "Manajemen Leadership & Senior",
    "Legal",
    "Manufaktur",
    "Marketing",
    "Operasional & Pelayanan Pelanggan",
    "Lainnya",
    "Product Management & Project Management",
    "Sains & Penelitian",
    "Industri Jasa",
    "Supply Chain, Logistik & Transportasi",
]

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

def _normalisasi_nama_kategori(nama_kategori_raw):
    """
    Mencocokkan nama kategori hasil scraping ke nama resmi dalam KATEGORI_GLINTS.
    Pencocokan dilakukan secara case-insensitive dan mengabaikan spasi berlebih.
    Mengembalikan nama resmi jika cocok, atau nama asli jika tidak ada yang cocok.
    """
    if not nama_kategori_raw or nama_kategori_raw == "-":
        return None

    nama_bersih = nama_kategori_raw.strip().lower()
    for resmi in KATEGORI_GLINTS:
        if resmi.lower() == nama_bersih:
            return resmi

    # Fallback: kembalikan nama asli jika tidak ada yang cocok
    return nama_kategori_raw.strip()


def sinkronisasi_folder_kategori():
    """
    Memindahkan item dari file JSON di root Job Archive ke subfolder kategori
    berdasarkan field Kategori_Utama pada setiap item.

    Aturan:
    - Item ber-kategori valid  → dipindah ke subfolder kategori, dihapus dari root.
    - Item tanpa kategori ("-") → tetap di root.
    - File root dihapus jika semua itemnya sudah dipindahkan.
    - Folder kategori kosong   → dihapus.
    """
    import shutil

    db_dir = get_database_permanen_dir()
    if not os.path.exists(db_dir):
        return

    # ── Langkah 1: Migrasi setiap file di root ke subfolder kategori ──
    for file_path in glob.glob(os.path.join(db_dir, "*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list) or not data:
                continue

            items_per_kat  = {}   # { nama_resmi: [item, ...] }
            items_tanpa_kat = []  # item tanpa kategori valid

            for item in data:
                kat = item.get("Kategori_Utama", "-")
                nama_resmi = _normalisasi_nama_kategori(kat)
                if nama_resmi:
                    items_per_kat.setdefault(nama_resmi, []).append(item)
                else:
                    items_tanpa_kat.append(item)

            if not items_per_kat:
                continue  # Tidak ada item ber-kategori, lewati

            base_name = os.path.basename(file_path)

            # Tulis item ke masing-masing subfolder kategori
            for kat_name, items in items_per_kat.items():
                folder_kat = os.path.join(db_dir, kat_name)
                os.makedirs(folder_kat, exist_ok=True)
                dst = os.path.join(folder_kat, base_name)

                # Baca data lama di subfolder (hindari duplikat)
                existing_kat = []
                if os.path.exists(dst):
                    try:
                        with open(dst, "r", encoding="utf-8") as f:
                            existing_kat = json.load(f)
                    except Exception:
                        existing_kat = []

                seen = {j.get("Link_Lowongan") for j in existing_kat
                        if j.get("Link_Lowongan") and j.get("Link_Lowongan") != "-"}
                for item in items:
                    lnk = item.get("Link_Lowongan", "-")
                    if lnk == "-" or lnk not in seen:
                        existing_kat.append(item)
                        if lnk != "-":
                            seen.add(lnk)

                with open(dst, "w", encoding="utf-8") as f:
                    json.dump(existing_kat, f, ensure_ascii=False, indent=4)
                print(f"  [Migrasi] {len(items)} item → '{kat_name}/{base_name}'")

            # Perbarui file root: hanya simpan item tanpa kategori
            if items_tanpa_kat:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(items_tanpa_kat, f, ensure_ascii=False, indent=4)
                print(f"  [Migrasi] '{base_name}' diperbarui: {len(items_tanpa_kat)} item tanpa kategori")
            else:
                os.remove(file_path)
                print(f"  [Migrasi] '{base_name}' dipindahkan sepenuhnya → dihapus dari root")

        except Exception as e:
            print(f"  [Migrasi] Error '{os.path.basename(file_path)}': {e}")

    # ── Langkah 2: Hapus folder kategori yang tidak punya file JSON ──
    for nama_resmi in KATEGORI_GLINTS:
        folder_kat = os.path.join(db_dir, nama_resmi)
        if os.path.exists(folder_kat) and os.path.isdir(folder_kat):
            isi_json = glob.glob(os.path.join(folder_kat, "*.json"))
            if not isi_json:
                try:
                    shutil.rmtree(folder_kat)
                    print(f"  [Kategori] Folder kosong dihapus: '{nama_resmi}'")
                except Exception as e:
                    print(f"  [Kategori] Gagal menghapus folder '{nama_resmi}': {e}")


def simpan_ke_database_permanen(job_data, source_filename):
    """
    Menyimpan data lowongan ke file koleksi permanen di folder 'Database Permanen'.
    Jika job_data memiliki Kategori_Utama yang valid, file disimpan langsung ke
    subfolder kategori. Jika tidak, file disimpan di root Job Archive.
    """
    db_dir = get_database_permanen_dir()

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Bersihkan nama file (buang prefix temp_ jika ada)
    base_name = os.path.basename(source_filename)
    if base_name.startswith("temp_"):
        base_name = base_name[5:]  # Buang 'temp_'

    # Tentukan folder tujuan berdasarkan Kategori_Utama
    kategori = _normalisasi_nama_kategori(job_data.get("Kategori_Utama", "-"))
    if kategori:
        target_dir = os.path.join(db_dir, kategori)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
    else:
        target_dir = db_dir  # Tanpa kategori → simpan di root

    full_path = os.path.join(target_dir, base_name)

    # Baca data lama jika ada
    existing_data = []
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            existing_data = []

    # Cek duplikat berdasarkan link
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
    
def catat_aktivitas(pesan, role="user"):
    """
    Mencatat aktivitas ke file terpisah berdasarkan role (user vs admin) tanpa memblokir UI.
    """
    def _catat():
        root = get_root_dir()
        dir_path = os.path.join(root, "database", "Database Permanen", "Dashboard")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        # Pisah nama file berdasarkan role
        file_name = "aktivitas_admin.json" if role == "admin" else "aktivitas_user.json"
        path = os.path.join(dir_path, file_name)
        
        aktivitas = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    aktivitas = json.load(f)
            except:
                aktivitas = []
        else:
            # Fallback backward compatibility: Coba migrasikan dari aktivitas.json lama jika ada
            old_path = os.path.join(dir_path, "aktivitas.json")
            if os.path.exists(old_path):
                try:
                    with open(old_path, "r", encoding="utf-8") as f:
                        semua = json.load(f)
                    aktivitas = [a for a in semua if a.get("role", "user") == role]
                except:
                    aktivitas = []
                
        # Tambahkan di awal agar yang terbaru muncul pertama
        aktivitas.insert(0, {
            "pesan": pesan,
            "waktu": "",
            "role": role
        })
        
        # Batasi maksimal 20 entri per file
        aktivitas = aktivitas[:20]
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(aktivitas, f, ensure_ascii=False, indent=4)
        except:
            pass

    threading.Thread(target=_catat, daemon=True).start()

def get_aktivitas(role="user"):
    """
    Mengambil daftar aktivitas terbaru berdasarkan role dari file terpisah.
    """
    root = get_root_dir()
    dir_path = os.path.join(root, "database", "Database Permanen", "Dashboard")
    file_name = "aktivitas_admin.json" if role == "admin" else "aktivitas_user.json"
    path = os.path.join(dir_path, file_name)
    
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
            
    # Fallback backward compatibility: Coba baca dari aktivitas.json lama
    old_path = os.path.join(dir_path, "aktivitas.json")
    if os.path.exists(old_path):
        try:
            with open(old_path, "r", encoding="utf-8") as f:
                semua = json.load(f)
            return [a for a in semua if a.get("role", "user") == role]
        except:
            return []
            
    return []

def get_all_saved_links():
    """Mengambil semua link lowongan yang ada di Job Archive (semua subfolder)."""
    db_dir = get_database_permanen_dir()
    if not os.path.exists(db_dir):
        return set()
    
    saved_links = set()
    # Cari semua file JSON di subfolder Job Archive
    file_paths = glob.glob(os.path.join(db_dir, "**", "*.json"), recursive=True)
    for fp in file_paths:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    lnk = item.get("Link_Lowongan")
                    if lnk and lnk != "-":
                        saved_links.add(lnk)
        except:
            continue
    return saved_links
