import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QToolTip
from PyQt5.QtGui import QCursor, QColor, QPainter
from PyQt5.QtCore import Qt, QSize

class PieChartWidget(QWidget):
    def __init__(self, parent=None, size_ratio=0.8):
        super().__init__(parent)
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
        
        self.colors = ["#2C687B", "#D9534F", "#5CB85C", "#F0AD4E", "#5BC0DE", "#6610F2", "#E83E8C", "#FD7E14", "#20C997", "#6F42C1"]
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
