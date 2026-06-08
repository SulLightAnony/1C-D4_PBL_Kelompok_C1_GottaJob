# Script ini untuk mendiagnosa masalah modul_kategorisasi
# Jalankan dari root project: python run_debug.py

import sys
import os

# Setup path yang sama seperti yang dilakukan app_router.py
base_dir = os.path.dirname(os.path.abspath(__file__))
pages_path = os.path.join(base_dir, "pages")
modul_path = os.path.join(pages_path, "Modul")

for p in [modul_path, pages_path]:
    if p not in sys.path:
        sys.path.insert(0, p)

print("=" * 60)
print(f"Project root: {base_dir}")
print(f"pages_path: {pages_path}")
print(f"modul_path: {modul_path}")
print()

# Coba import dan cek
try:
    from Modul.modul_kategorisasi import _get_dictionary_dir, KategorisasiSkill
    print("✓ Import berhasil")
    
    d = _get_dictionary_dir()
    print(f"dict_dir: {d}")
    print(f"Exists: {os.path.exists(d)}")
    print(f"universal.json: {os.path.exists(os.path.join(d, 'universal.json'))}")
    print(f"alias.json: {os.path.exists(os.path.join(d, 'alias.json'))}")
    print()
    
    # Buat fresh instance
    print("Membuat KategorisasiSkill()...")
    cat = KategorisasiSkill()
    print(f"soft_skill_keywords count: {len(cat.soft_skill_keywords)}")
    print(f"hard_skill_keywords count: {len(cat.hard_skill_keywords)}")
    print(f"alias_map count: {len(cat.alias_map)}")
    print()
    
    print(f"'teamwork' in soft: {'teamwork' in cat.soft_skill_keywords}")
    print(f"'communication' in soft: {'communication' in cat.soft_skill_keywords}")
    print()
    
    # Test klasifikasi
    test_skills = ["Teamwork", "Microsoft Office", "Communication", "Problem Solving", "Google Sheets"]
    for s in test_skills:
        r = cat._klasifikasi_satu(s)
        if r:
            print(f"  {s!r:30} → {r.kategori:12} [{r.confidence}] — {r.alasan}")
        else:
            print(f"  {s!r:30} → None")
            
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
