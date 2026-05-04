

import os
import re
import json
import glob
import unicodedata
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Data class hasil klasifikasi
# ---------------------------------------------------------------------------

@dataclass
class HasilKlasifikasi:
    skill_asli: str
    skill_normal: str
    kategori: str          # "hard_skill" | "soft_skill" | "position"
    confidence: str        # "high" | "medium" | "low"
    alasan: str            # penjelasan mengapa masuk kategori ini


# ---------------------------------------------------------------------------
# Helper: cari folder Skill Dictionary
# ---------------------------------------------------------------------------

def _get_dictionary_dir() -> str:
    """Mengembalikan path absolut ke folder Skill Dictionary."""
    # modul_kategorisasi.py ada di pages/Modul/
    # root proyek = 2 level ke atas
    modul_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(modul_dir))
    return os.path.join(root_dir, "database", "Database Permanen", "Skill Dictionary")


# ---------------------------------------------------------------------------
# Kelas utama
# ---------------------------------------------------------------------------

class KategorisasiSkill:

    def __init__(self, bidang: list = None):
        """
        Args:
            bidang: list nama bidang yang ingin dimuat (misal: ["it", "keuangan"]).
                    Jika None, semua bidang di folder bidang/ akan dimuat.
        """
        self.dict_dir = _get_dictionary_dir()

        # Data containers
        self.alias_map = {}
        self.soft_skill_keywords = set()
        self.ambiguous_keywords = {}
        self.position_patterns = []
        self._compiled_positions = []

        # Muat data dari JSON
        self._load_alias()
        self._load_universal()

    # ------------------------------------------------------------------
    # Loader: Alias
    # ------------------------------------------------------------------

    def _load_alias(self):
        path = os.path.join(self.dict_dir, "alias.json")
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.alias_map = data.get("alias", {})

    # ------------------------------------------------------------------
    # Loader: Universal (soft skills, posisi, ambigu)
    # ------------------------------------------------------------------

    def _load_universal(self):
        path = os.path.join(self.dict_dir, "universal.json")
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Soft skills
        self.soft_skill_keywords.update(data.get("soft_skills", []))

        # Position patterns
        patterns = data.get("position_patterns", [])
        self.position_patterns.extend(patterns)
        self._compiled_positions = [
            re.compile(p, re.IGNORECASE) for p in self.position_patterns
        ]

        # Ambiguous keywords
        amb = data.get("ambiguous_keywords", {})
        for word, rules in amb.items():
            self.ambiguous_keywords[word] = {
                "hard_indicators": set(rules.get("hard_indicators", [])),
                "soft_indicators": set(rules.get("soft_indicators", [])),
                "default": rules.get("default", "hard_skill"),
            }

    # ------------------------------------------------------------------
    # Normalisasi
    # ------------------------------------------------------------------

    def _normalize(self, text: str) -> str:
        text = text.strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        return self.alias_map.get(text, text)

    # ------------------------------------------------------------------
    # Pengecekan per kategori
    # ------------------------------------------------------------------

    def _is_soft_skill(self, text_lower: str) -> bool:
        return any(kw in text_lower for kw in self.soft_skill_keywords)

    def _is_position(self, text_lower: str) -> bool:
        return any(p.search(text_lower) for p in self._compiled_positions)

    def _resolve_ambiguous(self, text_lower: str) -> Optional[str]:
        for word, rules in self.ambiguous_keywords.items():
            if word in text_lower:
                for ctx in rules["hard_indicators"]:
                    if ctx in text_lower:
                        return "hard_skill"
                for ctx in rules["soft_indicators"]:
                    if ctx in text_lower:
                        return "soft_skill"
                return rules["default"]
        return None

    def _confidence(self, kategori: str, text_lower: str, match_count: int) -> str:
        if kategori == "soft_skill" and match_count > 1:
            return "high"
        if kategori == "position":
            return "high"
        return "medium" if match_count >= 1 else "low"

    # ------------------------------------------------------------------
    # Klasifikasi satu item
    # ------------------------------------------------------------------

    def _klasifikasi_satu(self, skill_raw: str) -> Optional[HasilKlasifikasi]:
        skill_clean = skill_raw.strip()
        if not skill_clean or skill_clean in ("-", "–", "•"):
            return None

        skill_normal = self._normalize(skill_clean)
        tl = skill_normal

        # Prioritas 1: Soft skill
        if self._is_soft_skill(tl):
            soft_matches = [kw for kw in self.soft_skill_keywords if kw in tl]
            return HasilKlasifikasi(
                skill_asli=skill_clean, skill_normal=skill_normal,
                kategori="soft_skill",
                confidence=self._confidence("soft_skill", tl, len(soft_matches)),
                alasan=f"Mengandung keyword soft skill: {', '.join(soft_matches[:3])}"
            )

        # Prioritas 2: Kata ambigu (resolusi kontekstual)
        resolved = self._resolve_ambiguous(tl)
        if resolved is not None:
            return HasilKlasifikasi(
                skill_asli=skill_clean, skill_normal=skill_normal,
                kategori=resolved, confidence="medium",
                alasan=f"Kata ambigu, diselesaikan via konteks → {resolved}"
            )

        # Prioritas 3: Posisi
        if self._is_position(tl):
            return HasilKlasifikasi(
                skill_asli=skill_clean, skill_normal=skill_normal,
                kategori="position", confidence="high",
                alasan="Cocok dengan pola jabatan"
            )

        # Fallback
        return HasilKlasifikasi(
            skill_asli=skill_clean, skill_normal=skill_normal,
            kategori="hard_skill", confidence="low",
            alasan="Tidak cocok pola apapun, diasumsikan hard skill"
        )

    # ------------------------------------------------------------------
    # API publik
    # ------------------------------------------------------------------

    def kategorikan(self, skill_list: list, dengan_detail: bool = False) -> dict:
        """
        Pisahkan list skill menjadi tiga kategori.

        Args:
            skill_list   : list string skill mentah
            dengan_detail: jika True, sertakan detail & confidence tiap item

        Returns:
            {
                "hard_skills": [...],
                "soft_skills": [...],
                "positions":   [...],
                "detail": [...]   # hanya jika dengan_detail=True
            }
        """
        result = {"hard_skills": [], "soft_skills": [], "positions": []}
        detail_list = []

        for skill in skill_list:
            item = self._klasifikasi_satu(skill)
            if item is None:
                continue
            if item.kategori == "soft_skill":
                result["soft_skills"].append(item.skill_asli)
            elif item.kategori == "position":
                result["positions"].append(item.skill_asli)
            else:
                result["hard_skills"].append(item.skill_asli)
            detail_list.append(item)

        if dengan_detail:
            result["detail"] = detail_list

        return result

    def debug(self, skill_list: list) -> None:
        """Cetak tabel debug klasifikasi ke stdout."""
        hasil = self.kategorikan(skill_list, dengan_detail=True)
        print(f"\n{'SKILL ASLI':<38} {'KATEGORI':<12} {'CONF':<8} ALASAN")
        print("-" * 95)
        for item in hasil["detail"]:
            print(
                f"{item.skill_asli:<38} "
                f"{item.kategori:<12} "
                f"{item.confidence:<8} "
                f"{item.alasan}"
            )
        print()
        print(f"Hard skills ({len(hasil['hard_skills'])}): {hasil['hard_skills']}")
        print(f"Soft skills ({len(hasil['soft_skills'])}): {hasil['soft_skills']}")
        print(f"Positions   ({len(hasil['positions'])}):   {hasil['positions']}")
        print(f"\n[INFO] Total data dimuat: "
              f"{len(self.soft_skill_keywords)} soft keywords, "
              f"{len(self.ambiguous_keywords)} kata ambigu, "
              f"{len(self.position_patterns)} pola posisi")


# ---------------------------------------------------------------------------
# Singleton & shortcut kompatibel dengan kode lama
# ---------------------------------------------------------------------------

# Default: muat semua bidang
categorizer = KategorisasiSkill()


def pisahkan_skill(skill_list: list) -> dict:
    """Shortcut kompatibel dengan versi sebelumnya."""
    return categorizer.kategorikan(skill_list)


# ---------------------------------------------------------------------------
# Demo / test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    contoh = [
        # Hard skills jelas
        "Python", "React.js", "MySQL", "Docker", "Microsoft Excel",
        "Machine Learning", "REST API", "Figma",

        # Soft skills jelas
        "Komunikasi", "Kepemimpinan", "Kemampuan Komunikasi",
        "Teamwork", "Berpikir Kritis", "Manajemen Waktu",

        # Posisi
        "Senior Backend Engineer", "Data Analyst",
        "Product Manager", "UI/UX Designer", "Staff Akuntansi",

        # Kasus ambigu
        "Database Management",
        "Project Management Tools",
        "Stress Management",
        "Detail Engineering Drawing",
        "Detail Oriented",
        "Supply Chain Management",
        "Data Analysis",
        "IT Administration",

        # Edge cases
        "Customer Support Skills",
        "Self Development",
        "Software Development Lifecycle",
        "Network Troubleshooting",
        "Attention to Detail",
    ]

    categorizer.debug(contoh)
