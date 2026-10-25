import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets


class InteractiveLabel(QtWidgets.QLabel):
    roi_updated = QtCore.pyqtSignal(str, tuple)  # mode ("start" or "goal"), (x, y, w, h)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: #000; color: #fff; font-weight: bold; font-size: 16px;")
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        
        self.drag_start_pos: QtCore.QPoint | None = None
        self.drag_end_pos: QtCore.QPoint | None = None
        self.current_mode: str | None = None
        self.orig_w: int = 800
        self.orig_h: int = 800
        self.is_warped: bool = False

    def set_frame(self, bgr_frame: np.ndarray, is_warped: bool = False) -> None:
        if bgr_frame is None:
            return
            
        h, w, _ = bgr_frame.shape
        self.orig_w, self.orig_h = w, h
        self.is_warped = is_warped
        
        rgb = bgr_frame[:, :, ::-1].copy()
        qimg = QtGui.QImage(rgb.data, w, h, 3 * w, QtGui.QImage.Format.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qimg)
        self.setPixmap(
            pix.scaled(
                self.size(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _map_to_image(self, pos: QtCore.QPoint) -> tuple[int, int] | None:
        if not self.pixmap() or not self.is_warped:
            return None
            
        px_w = self.pixmap().width()
        px_h = self.pixmap().height()
        ox = (self.width() - px_w) / 2
        oy = (self.height() - px_h) / 2
        
        rx = pos.x() - ox
        ry = pos.y() - oy
        
        if rx < 0 or rx > px_w or ry < 0 or ry > px_h:
            return None
            
        ix = int(rx * self.orig_w / px_w)
        iy = int(ry * self.orig_h / px_h)
        return (ix, iy)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if not self.is_warped:
            return
            
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            self.current_mode = "start"
        elif ev.button() == QtCore.Qt.MouseButton.RightButton:
            self.current_mode = "goal"
        else:
            self.current_mode = None
            return
            
        mapped = self._map_to_image(ev.pos())
        if mapped:
            self.drag_start_pos = ev.pos()
            self.drag_end_pos = ev.pos()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.drag_start_pos and self.current_mode:
            self.drag_end_pos = ev.pos()
            self.update()

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if not self.drag_start_pos or not self.current_mode:
            return
            
        mapped_start = self._map_to_image(self.drag_start_pos)
        mapped_end = self._map_to_image(ev.pos())
        
        mode = self.current_mode
        self.drag_start_pos = None
        self.drag_end_pos = None
        self.current_mode = None
        self.update()
        
        if mapped_start and mapped_end:
            x1, y1 = mapped_start
            x2, y2 = mapped_end
            
            if mode == "start":
                thickness = 15
                if abs(x2 - x1) > abs(y2 - y1):
                    # Horizontal tripwire
                    x, y = min(x1, x2), y1 - thickness // 2
                    w, h = max(abs(x2 - x1), 1), thickness
                else:
                    # Vertical tripwire
                    x, y = x1 - thickness // 2, min(y1, y2)
                    w, h = thickness, max(abs(y2 - y1), 1)
            else:
                x, y = min(x1, x2), min(y1, y2)
                w, h = max(abs(x2 - x1), 1), max(abs(y2 - y1), 1)
            
            # Require at least 20 pixels of length to register
            if max(w, h) > 20:
                self.roi_updated.emit(mode, (x, y, w, h))

    def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
        super().paintEvent(ev)
        if self.drag_start_pos and self.drag_end_pos and self.current_mode:
            painter = QtGui.QPainter(self)
            color = QtGui.QColor(0, 255, 0) if self.current_mode == "start" else QtGui.QColor(255, 0, 0)
            pen = QtGui.QPen(color, 2, QtCore.Qt.PenStyle.DashLine)
            painter.setPen(pen)
            
            x1, y1 = self.drag_start_pos.x(), self.drag_start_pos.y()
            x2, y2 = self.drag_end_pos.x(), self.drag_end_pos.y()
            
            if self.current_mode == "start":
                if abs(x2 - x1) > abs(y2 - y1):
                    y2 = y1  # Force visual line to be horizontal
                else:
                    x2 = x1  # Force visual line to be vertical
            
            # Bound drawing to visible label area
            w, h = self.width(), self.height()
            x2 = max(0, min(x2, w))
            y2 = max(0, min(y2, h))
            
            rect = QtCore.QRect(QtCore.QPoint(x1, y1), QtCore.QPoint(x2, y2))
            painter.drawRect(rect)
            painter.end()
