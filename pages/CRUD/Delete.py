

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
