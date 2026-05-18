import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QToolTip
from PyQt5.QtGui import QCursor, QColor, QPainter
from PyQt5.QtCore import Qt, QSize

def dapatkan_warna_visualisasi():
    """Mengembalikan daftar warna terstandarisasi untuk visualisasi data."""
    return ["#2C687B", "#D9534F", "#5CB85C", "#F0AD4E", "#5BC0DE", "#6610F2", "#E83E8C", "#FD7E14", "#20C997", "#6F42C1"]

class HorizontalBarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        
        # Legend/Subtitle Area
        self.legend_layout = QHBoxLayout()
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setSpacing(8)
        
        self.colors = dapatkan_warna_visualisasi()
        main_color = self.colors[0] # "#2C687B"
        
        color_box = QLabel()
        color_box.setFixedSize(14, 14)
        color_box.setStyleSheet(f"background-color: {main_color}; border-radius: 3px;")
        
        legend_text = QLabel("Jumlah lowongan yang membutuhkan skill")
        legend_text.setStyleSheet("font-size: 13px; color: #555555; font-weight: 500; background-color: transparent;")
        
        self.legend_layout.addWidget(color_box)
        self.legend_layout.addWidget(legend_text)
        self.legend_layout.addStretch()
        self.main_layout.addLayout(self.legend_layout)
        
        # Matplotlib Figure & Canvas
        self.figure, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.figure.patch.set_alpha(0.0)
        self.ax.patch.set_alpha(0.0)
        self.canvas.setStyleSheet("background-color: transparent;")
        
        from PyQt5.QtWidgets import QSizePolicy
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(300, 200)
        self.main_layout.addWidget(self.canvas)
        
        self.bars = []
        self.tooltips = []
        self.hovered_index = -1
        
        # Hubungkan hover event
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas.mpl_connect('axes_leave_event', self.on_leave)
        
    def set_data(self, top_skills, total_lowongan=0):
        """
        Menerima list of tuple: [(skill_name, jumlah), ...]
        """
        self.ax.clear()
        self.bars = []
        self.tooltips = []
        self.hovered_index = -1
        
        if not top_skills:
            self.canvas.draw()
            return
            
        # Balik urutan agar skill teratas berada di paling atas grafik
        top_skills = list(reversed(top_skills))
        
        skills = [item[0] for item in top_skills]
        values = [item[1] for item in top_skills]
        
        # Gunakan kombinasi warna cantik untuk tiap bar
        bar_colors = [self.colors[i % len(self.colors)] for i in range(len(skills))]
        
        self.bars = self.ax.barh(
            skills, 
            values, 
            color=bar_colors, 
            height=0.55, 
            edgecolor='none'
        )
        
        # Styling axis
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#E2E8F0')
        self.ax.spines['bottom'].set_color('#E2E8F0')
        
        # Grid horizontal
        self.ax.grid(axis='x', linestyle=':', alpha=0.5, color='#CBD5E1')
        self.ax.set_axisbelow(True)
        
        # Tick labels styling
        self.ax.tick_params(colors='#4A5568', labelsize=10)
        for label in self.ax.get_yticklabels():
            label.set_fontweight('medium')
            label.set_fontsize(10)
            
        # Tooltips data
        for skill_name, jumlah in top_skills:
            # Cari warna khusus untuk skill ini
            idx = skills.index(skill_name)
            col = bar_colors[idx]
            if total_lowongan > 0:
                tooltip_text = f"<span style='font-size:14px; font-weight:bold; color:#1E3A4A;'>{skill_name}</span><br><span style='color:{col}; font-size:16px;'>■</span> <b>{jumlah} dari {total_lowongan} lowongan</b>"
            else:
                tooltip_text = f"<span style='font-size:14px; font-weight:bold; color:#1E3A4A;'>{skill_name}</span><br><span style='color:{col}; font-size:16px;'>■</span> <b>{jumlah} lowongan</b>"
            self.tooltips.append(tooltip_text)
            
        # Atur batas X agar terlihat pas (jumlah absolute)
        max_val = max(values) if values else 10
        buffer = max(2, int(max_val * 0.15))
        self.ax.set_xlim(0, max_val + buffer)
        
        # Rapikan layout
        self.figure.tight_layout()
        self.canvas.draw()
        
    def on_hover(self, event):
        if not self.bars:
            return
            
        found = False
        for i, bar in enumerate(self.bars):
            if bar.contains(event)[0]:
                found = True
                if self.hovered_index != i:
                    self.hovered_index = i
                    self.highlight_bar(i)
                    
                    # Tampilkan tooltip PyQt5
                    global_pos = QCursor.pos()
                    QToolTip.showText(global_pos, self.tooltips[i], self)
                break
                
        if not found and self.hovered_index != -1:
            self.on_leave(event)
            
    def on_leave(self, event):
        if self.hovered_index != -1:
            self.hovered_index = -1
            self.highlight_bar(-1)
            QToolTip.hideText()
            
    def highlight_bar(self, index):
        for i, bar in enumerate(self.bars):
            if index == -1 or index == i:
                bar.set_alpha(1.0)
            else:
                bar.set_alpha(0.4)
        self.canvas.draw_idle()

class PieChartWidget(QWidget):
    def __init__(self, parent=None, size_ratio=0.8):
        super().__init__(parent)
        self.setStyleSheet("""
            QToolTip {
                background-color: #FFFFFF;
                color: #1E3A4A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
        """)
        self.size_ratio = size_ratio
        
        # Layout utama
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Canvas Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(3, 3), dpi=100) # Diperkecil dari 4x4
        self.canvas = FigureCanvas(self.figure)
        self.figure.patch.set_alpha(0.0)
        self.ax.patch.set_alpha(0.0)
        self.canvas.setStyleSheet("background-color:transparent;")
        self.ax.axis('equal')
        self.ax.axis('off')
        
        # Atur Size Policy agar canvas bisa mengecil jika diperlukan
        from PyQt5.QtWidgets import QSizePolicy
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumSize(200, 200) # Batas bawah agar tidak terlalu hancur
        
        self.main_layout.addWidget(self.canvas)

        # Legend Area (Scrollable)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        self.scroll.setMaximumHeight(120) # Diperkecil dari 180
        
        self.legend_container = QWidget()
        self.legend_container.setStyleSheet("background: transparent;")
        self.legend_layout = QVBoxLayout(self.legend_container)
        self.legend_layout.setContentsMargins(30, 0, 30, 10)
        self.legend_layout.setSpacing(6)
        self.legend_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.legend_container)
        self.main_layout.addWidget(self.scroll)
        
        self.colors = dapatkan_warna_visualisasi()
        self.wedges = []
        self.tooltips = []
        self.hovered_index = -1
        
        # Hubungkan event hover dari Matplotlib
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas.mpl_connect('axes_leave_event', self.on_leave)

    def set_data(self, processed_data):
        self.ax.clear()
        self.ax.axis('equal')
        self.ax.axis('off')
        
        self.wedges = []
        self.tooltips = []
        self.hovered_index = -1
        
        # Bersihkan legenda lama
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not processed_data:
            self.canvas.draw()
            return
            
        # Cek apakah format data adalah format kategori (Admin Dashboard)
        # Format: { "Nama Kategori": { "jumlah": X, "persentase": Y } }
        is_category_format = False
        first_val = list(processed_data.values())[0]
        if isinstance(first_val, dict) and "persentase" in first_val:
            is_category_format = True
            
        if is_category_format:
            sizes = []
            for kat, info in processed_data.items():
                sizes.append(info["persentase"])
                
            self.wedges, _ = self.ax.pie(
                sizes,
                colors=self.colors[:len(sizes)],
                wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
            )
            
            for i, (kat, info) in enumerate(processed_data.items()):
                color_hex = self.colors[i % len(self.colors)]
                perc = info["persentase"]
                jumlah = info["jumlah"]
                
                # Tooltip
                tooltip_text = f"<span style='font-size:14px; font-weight:bold; color:#1E3A4A;'>{kat}</span><br><span style='color:{color_hex}; font-size:16px;'>■</span> <b>{jumlah} lowongan ({perc}%)</b>"
                self.tooltips.append(tooltip_text)
                
                # Legend Item
                item_widget = QWidget()
                item_lay = QHBoxLayout(item_widget)
                item_lay.setContentsMargins(0, 0, 0, 0)
                item_lay.setSpacing(12)
                
                color_box = QLabel()
                color_box.setFixedSize(16, 16)
                color_box.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px;")
                
                perc_lbl = QLabel(f"<b>{perc}%</b>")
                perc_lbl.setFixedWidth(55)
                perc_lbl.setStyleSheet("font-size: 16px; color: #1E3A4A; background-color: transparent;")
                
                skills_lbl = QLabel(f"{kat} ({jumlah} lowongan)")
                skills_lbl.setStyleSheet("font-size: 16px; color: #4A5568; background-color: transparent;")
                skills_lbl.setWordWrap(True)
                
                item_lay.addWidget(color_box)
                item_lay.addWidget(perc_lbl)
                item_lay.addWidget(skills_lbl, stretch=1)
                
                self.legend_layout.addWidget(item_widget)
                
            self.canvas.draw()
            return
            
        sizes = list(processed_data.keys())
        
        # Buat Donut Chart
        self.wedges, _ = self.ax.pie(
            sizes,
            colors=self.colors[:len(sizes)],
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
        )
        
        # Siapkan tooltip teks dan item legenda untuk tiap potongan
        for i, (perc, skills) in enumerate(processed_data.items()):
            color_hex = self.colors[i % len(self.colors)]
            
            # Tooltip
            label_skills_br = "<br>".join([f"• {s}" for s in skills])
            tooltip_text = f"<span style='color:{color_hex}; font-size:16px;'>■</span> <b>{perc}%</b><br>{label_skills_br}"
            self.tooltips.append(tooltip_text)
            
            # Legend Item
            item_widget = QWidget()
            item_lay = QHBoxLayout(item_widget)
            item_lay.setContentsMargins(0, 0, 0, 0)
            item_lay.setSpacing(12)
            
            color_box = QLabel()
            color_box.setFixedSize(16, 16)
            color_box.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px;")
            
            perc_lbl = QLabel(f"<b>{perc}%</b>")
            perc_lbl.setFixedWidth(55)
            perc_lbl.setStyleSheet("font-size: 16px; color: #1E3A4A;")
            
            skills_txt = ", ".join(skills)
            skills_lbl = QLabel(skills_txt)
            skills_lbl.setStyleSheet("font-size: 16px; color: #4A5568;")
            skills_lbl.setWordWrap(True)
            
            item_lay.addWidget(color_box)
            item_lay.addWidget(perc_lbl)
            item_lay.addWidget(skills_lbl, stretch=1)
            
            self.legend_layout.addWidget(item_widget)
            
        self.canvas.draw()

    def on_hover(self, event):
        if not self.wedges:
            return
            
        # Periksa potongan mana yang di-hover
        found = False
        for i, wedge in enumerate(self.wedges):
            if wedge.contains(event)[0]:
                found = True
                if self.hovered_index != i:
                    self.hovered_index = i
                    self.highlight_wedge(i)
                    
                    # Tampilkan tooltip PyQt5
                    global_pos = QCursor.pos()
                    QToolTip.showText(global_pos, self.tooltips[i], self)
                break
                
        if not found and self.hovered_index != -1:
            self.on_leave(event)

    def on_leave(self, event):
        if self.hovered_index != -1:
            self.hovered_index = -1
            self.highlight_wedge(-1)
            QToolTip.hideText()

    def highlight_wedge(self, index):
        for i, wedge in enumerate(self.wedges):
            if index == -1 or index == i:
                wedge.set_alpha(1.0)
            else:
                wedge.set_alpha(0.3)
        self.canvas.draw_idle()
