from PyQt5.QtWidgets import QDialog
from CRUD.Shared import simpan_data

def gui_perbarui_data(page, JobDialogClass, job_data):
    """
    Fungsi logika untuk memperbarui (edit) data pekerjaan via GUI.
    """
    dialog = JobDialogClass(page, job_data=job_data)
    if dialog.exec_() == QDialog.Accepted:
        updated_data = dialog.get_data()
        for i, j in enumerate(page.data):
            if j.get("id") == job_data.get("id"):
                page.data[i] = updated_data
                break
        simpan_data(page.data)
        page.load_data()
