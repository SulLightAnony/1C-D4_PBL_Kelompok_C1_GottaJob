import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolTip
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

class PieChartWidget(QWidget):
    def __init__(self, parent=None, size_ratio=0.8):
        super().__init__(parent)
        self.size_ratio = size_ratio
        
        # Inisialisasi Matplotlib Figure & Canvas
        self.figure, self.ax = plt.subplots(figsize=(4, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        # Buat background transparan
        self.figure.patch.set_alpha(0.0)
        self.ax.patch.set_alpha(0.0)
        self.canvas.setStyleSheet("background-color:transparent;")
        self.ax.axis('equal')
        self.ax.axis('off')
        
        # Tambahkan canvas ke dalam layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
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
        
        # Siapkan tooltip teks untuk tiap potongan
        for i, (perc, skills) in enumerate(processed_data.items()):
            color_hex = self.colors[i % len(self.colors)]
            label_skills = "<br>".join([f"• {s}" for s in skills])
            tooltip_text = f"<span style='color:{color_hex}; font-size:16px;'>■</span> <b>{perc}%</b><br>{label_skills}"
            self.tooltips.append(tooltip_text)
            
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
