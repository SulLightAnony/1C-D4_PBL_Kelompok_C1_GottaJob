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
