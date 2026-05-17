"""
FlowLayout — custom QLayout yang menyusun widget secara
mengalir (wrap) layaknya teks, mendukung multi-kolom
dengan lebar seragam.
"""
from PyQt5.QtWidgets import QLayout
from PyQt5.QtCore import Qt, QSize, QRect


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1, uniform_width=True):
        super(FlowLayout, self).__init__(parent)
        self.itemList = []
        self.uniform_width = uniform_width
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def removeWidget(self, widget):
        """Hapus widget dari itemList secara eksplisit."""
        for i, item in enumerate(self.itemList):
            if item.widget() is widget:
                self.itemList.pop(i)
                self.invalidate()
                return

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        if not self.itemList:
            return 0

        # Parameter untuk layouting
        spaceX = self.spacing()
        spaceY = self.spacing()
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        available_width = rect.width()

        if self.uniform_width:
            # Mode A: Lebar Seragam (untuk grid kartu)
            ref_min_w = self.itemList[0].minimumSize().width()
            if ref_min_w <= 0: ref_min_w = 320
            
            cols = max(1, (available_width + spaceX) // (ref_min_w + spaceX))
            item_w = (available_width - (cols - 1) * spaceX) // cols

            for i, item in enumerate(self.itemList):
                item_h = item.sizeHint().height()
                if not testOnly:
                    item.setGeometry(QRect(x, y, item_w, item_h))

                x += item_w + spaceX
                lineHeight = max(lineHeight, item_h)

                if (i + 1) % cols == 0:
                    x = rect.x()
                    y += lineHeight + spaceY
                    lineHeight = 0
            
            # Kembalikan tinggi total
            if len(self.itemList) % cols != 0:
                return y + lineHeight - rect.y()
            else:
                return y - rect.y() - spaceY if y > rect.y() else 0
        
        else:
            # Mode B: Lebar Sesuai Isi (untuk tag/pills)
            for item in self.itemList:
                item_w = item.sizeHint().width()
                item_h = item.sizeHint().height()

                if x + item_w > rect.right() and lineHeight > 0:
                    x = rect.x()
                    y = y + lineHeight + spaceY
                    lineHeight = 0

                if not testOnly:
                    item.setGeometry(QRect(x, y, item_w, item_h))

                x += item_w + spaceX
                lineHeight = max(lineHeight, item_h)

            return y + lineHeight - rect.y()
