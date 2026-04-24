import json
import os
import uuid
from datetime import datetime

class CVDataManager:
    def __init__(self):
        # Jalur file disesuaikan dengan struktur folder projek
        # Mengasumsikan skrip dijalankan dari root (main.py)
        self.db_path = os.path.join("database", "curiculum-vitae.json")
        self.temp_path = os.path.join("database", "curiculum-vitae-temp.json")
        
        # Pastikan folder database ada
        os.makedirs("database", exist_ok=True)
        
        # Inisialisasi file jika belum ada
        self._ensure_file_exists(self.db_path, [])
        self._ensure_file_exists(self.temp_path, {})

    def _ensure_file_exists(self, path, default_content):
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump(default_content, f, indent=4)

    # --- LOGIKA DATABASE UTAMA ---
    
    def get_all_cv(self):
        """Mengambil semua daftar CV yang sudah disimpan."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Jika file ada tapi isinya kosong/corrupt, kembalikan list kosong
            return []

    def save_final_cv(self, cv_data, template_id):
        """Menyimpan CV dari temp/form ke database utama."""
        all_cv = self.get_all_cv()
        
        # Jika CV baru (tidak punya ID), buatkan ID unik
        if not cv_data.get("cv_id"):
            cv_data["cv_id"] = str(uuid.uuid4())[:8]
            cv_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cv_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        cv_data["template_id"] = template_id
        
        # Update jika ID sudah ada, atau tambah jika baru
        existing_index = next((i for i, item in enumerate(all_cv) if item["cv_id"] == cv_data["cv_id"]), None)
        
        if existing_index is not None:
            all_cv[existing_index] = cv_data
        else:
            all_cv.insert(0, cv_data) # Taruh di paling atas

        with open(self.db_path, 'w') as f:
            json.dump(all_cv, f, indent=4)
        
        self.clear_temp() # Bersihkan temp setelah simpan permanen
        return cv_data["cv_id"]

    def duplicate_cv(self, cv_id):
        """Menyalin data CV yang sudah ada."""
        all_cv = self.get_all_cv()
        original = next((item for item in all_cv if item["cv_id"] == cv_id), None)
        
        if original:
            new_copy = original.copy()
            new_copy["cv_id"] = str(uuid.uuid4())[:8]
            new_copy["cv_name"] = f"{original['cv_name']} (1)"
            new_copy["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            all_cv.insert(0, new_copy)
            
            with open(self.db_path, 'w') as f:
                json.dump(all_cv, f, indent=4)
            return True
        return False

    def delete_cv(self, cv_id):
        """Menghapus CV dari database."""
        all_cv = self.get_all_cv()
        all_cv = [item for item in all_cv if item["cv_id"] != cv_id]
        
        with open(self.db_path, 'w') as f:
            json.dump(all_cv, f, indent=4)

    # --- LOGIKA DATA SEMENTARA (TEMP) ---

    def get_temp_data(self):
        """Membaca data draf yang sedang dikerjakan."""
        try:
            with open(self.temp_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Jika file kosong, kembalikan dictionary kosong
            return {}

    def save_to_temp(self, data):
        """Menyimpan setiap perubahan input secara realtime ke file draf."""
        with open(self.temp_path, 'w') as f:
            json.dump(data, f, indent=4)

    def clear_temp(self):
        """Mengosongkan file draf."""
        with open(self.temp_path, 'w') as f:
            json.dump({}, f, indent=4)