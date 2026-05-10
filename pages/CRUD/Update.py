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

def proses_update_job(job_id, form_data, current_data):
    from PyQt5.QtCore import QDate

    judul = form_data.get('judul', '').strip()
    perusahaan = form_data.get('perusahaan', '').strip()
    
    if not judul:
        return False, "Judul Pekerjaan wajib diisi!", current_data
    if not perusahaan:
        return False, "Nama Perusahaan wajib diisi!", current_data

    # Validasi Tanggal Kadaluarsa
    selected_date = form_data.get('date', QDate.currentDate())
    if selected_date <= QDate.currentDate():
        return False, "Tanggal Kadaluarsa tidak boleh hari ini atau di masa lalu!", current_data

    g_min = form_data.get('gaji_min', '').strip()
    g_max = form_data.get('gaji_max', '').strip()
    rentang_final = f"{g_min}-{g_max}" if g_min and g_max else (g_min or g_max or "-")

    skills_list = form_data.get('skills', [])
    skills_str = "|".join(skills_list)

    # Cari data lama untuk mempertahankan field non-form (seperti Is_lamar)
    old_job = next((j for j in current_data if j.get("id") == job_id), {})
    
    new_data = {
        "id": job_id,
        "Judul_Pekerjaan": judul,
        "Nama_Perusahaan": perusahaan,
        "Jenis_Pekerjaan": form_data.get('jenis', ''),
        "Lokasi": form_data.get('lokasi', '').strip(),
        "Rentang_Gaji": rentang_final,
        "Skills": skills_str,
        "Link_Lowongan": form_data.get('link', '').strip(),
        "Deskripsi_Pekerjaan": form_data.get('desc', '').strip(),
        "Benefit_Pekerjaan": form_data.get('benefit', '').strip(),
        "Kualifikasi_Persyaratan": form_data.get('kualifikasi', '').strip(),
        "Kategori": form_data.get('kategori', '').strip(),
        "Tanggal_Kadaluarsa": f"{selected_date.day():02d}/{selected_date.month():02d}/{selected_date.year()}",
        "Is_lamar": old_job.get("Is_lamar", False)
    }

    for i, job in enumerate(current_data):
        if job.get("id") == job_id:
            current_data[i] = new_data
            break

    return True, "Lowongan berhasil diedit!", current_data
