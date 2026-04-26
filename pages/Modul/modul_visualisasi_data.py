import math
from PyQt5.QtWidgets import QWidget, QToolTip
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRectF

class PieChartWidget(QWidget):
    def __init__(self, parent=None, size_ratio=0.5):
        super().__init__(parent)
        self.data = []
        self.size_ratio = size_ratio
        self.colors = [
            QColor("#2C687B"), QColor("#D9534F"), QColor("#5CB85C"),
            QColor("#F0AD4E"), QColor("#5BC0DE"), QColor("#6610F2"),
            QColor("#E83E8C"), QColor("#FD7E14"), QColor("#20C997"), QColor("#6F42C1")
        ]
        self.setMinimumHeight(250)
        self.setMouseTracking(True)
        self.hovered_index = -1

    def set_data(self, processed_data):
        self.data = []
        if not processed_data:
            self.update()
            return
            
        total = sum(processed_data.keys())
        
        i = 0
        for perc, skills in processed_data.items():
            color = self.colors[i % len(self.colors)]
            
            # Format label tooltip (Gunakan <br> agar rapi di dalam HTML Tooltip)
            label_skills = "<br>".join([f"• {s}" for s in skills])
            
            # Tambahkan kotak warna menggunakan karakter HTML span
            color_hex = color.name()
            tooltip_text = f"<span style='color:{color_hex}; font-size:16px;'>■</span> <b>{perc}%</b><br>{label_skills}"
            
            span_deg = (perc / total) * 360
            
            self.data.append({
                "perc": perc,
                "span_deg": span_deg,
                "tooltip": tooltip_text,
                "color": color
            })
            i += 1
            
        self.update()

    def mouseMoveEvent(self, event):
        if not self.data:
            return
            
        size = min(self.width(), self.height()) * self.size_ratio
        center_x = self.width() / 2
        center_y = self.height() / 2
        outer_radius = size / 2
        inner_radius = outer_radius * 0.55 # Ukuran lubang donut
        
        dx = event.x() - center_x
        dy = event.y() - center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        new_hover = -1
        
        if inner_radius <= distance <= outer_radius:
            # Hitung sudut mouse (0 di arah jam 3, berlawanan jarum jam)
            angle = math.degrees(math.atan2(-dy, dx))
            if angle < 0: angle += 360
            
            # Map ke sistem sudut kita (0 di jam 12, searah jarum jam)
            mapped_angle = 90 - angle
            if mapped_angle < 0: mapped_angle += 360
            
            # Cari slice mana yang di-hover
            current_angle = 0
            for i, item in enumerate(self.data):
                if current_angle <= mapped_angle <= current_angle + item["span_deg"]:
                    new_hover = i
                    break
                current_angle += item["span_deg"]
                
        if new_hover != self.hovered_index:
            self.hovered_index = new_hover
            self.update()
            
            if self.hovered_index != -1:
                QToolTip.showText(event.globalPos(), self.data[self.hovered_index]["tooltip"], self)
            else:
                QToolTip.hideText()

    def leaveEvent(self, event):
        self.hovered_index = -1
        QToolTip.hideText()
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Diagram lebih kecil & terpusat (Samakan dengan mouseMoveEvent)
        size = min(self.width(), self.height()) * self.size_ratio
        pos_x = (self.width() - size) / 2
        pos_y = (self.height() - size) / 2
        rect = QRectF(pos_x, pos_y, size, size)
        
        start_angle = 90 * 16 # Mulai jam 12
        
        for i, item in enumerate(self.data):
            span_angle = -int(item["span_deg"] * 16) # Negatif = searah jarum jam
            
            color = item["color"]
            if self.hovered_index != -1 and self.hovered_index != i:
                # Meredupkan warna lain saat ada yang di-hover
                color = color.lighter(150)
                
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.white, 2)) # Garis batas putih
            painter.drawPie(rect, start_angle, span_angle)
            
            start_angle += span_angle
            
        # Potong bagian tengah untuk efek Donut
        inner_size = size * 0.55
        inner_rect = QRectF((self.width() - inner_size) / 2, (self.height() - inner_size) / 2, inner_size, inner_size)
        painter.setBrush(QBrush(QColor("#FFFFFF"))) # Warna background card
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(inner_rect)
