from PyQt5.QtWidgets import QMessageBox
from CRUD.Shared import simpan_data

def gui_hapus_data_single(page, job_data):
    """
    Fungsi logika untuk menghapus satu data pekerjaan via GUI.
    """
    reply = QMessageBox.question(page, 'Konfirmasi Hapus', "Yakin ingin menghapus lowongan ini?", QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.Yes:
        page.data = [j for j in page.data if j.get("id") != job_data.get("id")]
        simpan_data(page.data)
        page.load_data()

def gui_hapus_data_massal(page):
    """
    Fungsi logika untuk menghapus beberapa data pekerjaan yang dipilih (bulk delete).
    """
    reply = QMessageBox.question(page, 'Konfirmasi Hapus Massal', f"Yakin ingin menghapus {len(page.selected_ids)} lowongan terpilih?", QMessageBox.Yes | QMessageBox.No)
    if reply == QMessageBox.Yes:
        page.data = [j for j in page.data if j.get("id") not in page.selected_ids]
        simpan_data(page.data)
        page.load_data()

def proses_delete_job(job_id, current_data):
    """
    Menghapus satu job berdasarkan ID dan mengembalikan data terbaru.
    """
    new_data = [j for j in current_data if j.get("id") != job_id]
    
    # Cari judul pekerjaan untuk dicatat di aktivitas
    judul = "Unknown"
    for j in current_data:
        if j.get("id") == job_id:
            judul = j.get("Judul_Pekerjaan", "Unknown")
            break
            
    return True, f"<b>Lowongan Dihapus</b><br>{judul}", new_data

def proses_delete_massal(job_ids, current_data):
    """
    Menghapus beberapa job sekaligus berdasarkan daftar ID.
    """
    if not job_ids:
        return False, "Tidak ada lowongan yang dipilih", current_data
        
    jumlah = len(job_ids)
    new_data = [j for j in current_data if j.get("id") not in job_ids]
    return True, f"<b>Lowongan Dihapus</b><br>{jumlah} data lowongan", new_data
