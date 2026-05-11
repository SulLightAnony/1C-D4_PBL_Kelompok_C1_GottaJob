"""
Konstanta path untuk aset (icon, gambar) yang digunakan
oleh modul-modul di folder Job Posting.
"""
import os

_here = os.path.dirname(os.path.abspath(__file__))
_pages_dir = os.path.dirname(_here)
_root_dir = os.path.dirname(_pages_dir)

# Job Archive assets
down_icon_path = os.path.join(_root_dir, "assets", "Job Archive", "down.png").replace("\\", "/")
refresh_icon_path = os.path.join(_root_dir, "assets", "Job Archive", "refresh.png")

# Job Posting assets
post_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "post.png")
trash_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "trash-can.png")
trash_icon_card_path = os.path.join(_root_dir, "assets", "Job Posting", "trash-can2.png")
currency_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "save-money.png")
edit_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "edit.png")
location_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "gps.png")
location_detail_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "location.png")
company_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "building.png")
green_check_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "green_check.png")
check_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "check.png")
search_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "search.png")
plus_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "plus.png")
send_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "send.png")
checked_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "checked.png")
calendar_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "calendar.png")
link_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "link.png")
suitcase_icon_path = os.path.join(_root_dir, "assets", "Job Posting", "suitcase.png")
