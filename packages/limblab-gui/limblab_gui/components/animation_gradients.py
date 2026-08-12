
# pyright: reportOptionalMemberAccess=false
# pyright: ignore[reportAttributeAccessIssue]

import math

from limblab.design_tokens import theme
from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
)
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
)


class AnimatedGradientWidget(QWidget):
    """A QWidget that paints an animated linear gradient background."""

    def __init__(self, parent=None, speed: float = 0.0003):
        super().__init__(parent)
        self.phase = 0.0
        self.speed = speed
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(30)

    def _on_timer(self):
        self.phase += self.speed
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        cx = r.center().x()
        cy = r.center().y()
        dx = math.cos(self.phase) * r.width() / 2
        dy = math.sin(self.phase) * r.height() / 2

        grad = QLinearGradient(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
        c1 = QColor(theme("palette.primary", "#0D7C66"))
        c2 = QColor(theme("palette.secondary", "#8E7FD6"))
        c3 = QColor(theme("palette.accent", "#5FBF9F"))

        grad.setColorAt(0.0, c1)
        grad.setColorAt(0.5, c2)
        grad.setColorAt(1.0, c3)

        painter.fillRect(r, grad)
        painter.end()


class AnimatedGradientLabel(QLabel):
    """A QLabel that paints its text filled with an animated linear gradient."""

    def __init__(self, text: str = "", parent=None, speed: float = 0.0003):
        super().__init__(text, parent)
        self.phase = 0.0
        self.speed = speed
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(30)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _on_timer(self):
        self.phase += self.speed
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        cx = r.center().x()
        cy = r.center().y()
        dx = math.cos(self.phase) * r.width() / 2
        dy = math.sin(self.phase) * r.height() / 2

        grad = QLinearGradient(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
        c1 = QColor(theme("palette.primary", "#0D7C66"))
        c2 = QColor(theme("palette.secondary", "#8E7FD6"))
        c3 = QColor(theme("palette.accent", "#5FBF9F"))
        grad.setColorAt(0.0, c1)
        grad.setColorAt(0.5, c2)
        grad.setColorAt(1.0, c3)

        pen = QPen(QBrush(grad), 0)
        painter.setPen(pen)

        # Apply themed font size if available
        font = self.font()
        try:
            size = int(theme("typography.fontSizeHero", 100))
        except Exception:
            size = 100
        font.setPointSize(size)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(r, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()

