from limblab.design import theme
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


class TerminalPaperWidget(QWidget):
    """Terminal-like paper card that accepts custom text content."""

    def __init__(self, text: str | None = None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(520)
        self.setMinimumHeight(220)
        self.setStyleSheet("""
            QWidget {
                color: #E8EDF3;
            }
        """)

        if text is None:
            text = (
                "<- ->    use arrows to reduce/increase opacity\n"
                "x        toggle mesh visibility\n"
                "w        toggle wireframe/surface style\n"
                "l        toggle surface edges visibility\n"
                "1-3      cycle surface color\n"
                "k        cycle available lighting styles\n"
                "r        reset camera position\n"
                "shift    pan\n"
                "ctl/cmd  rotate over an axis"
            )

        self.text = text

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        titlebar = QWidget(self)
        titlebar.setFixedHeight(30)
        titlebar.setStyleSheet(
            "QWidget { background: rgba(255, 255, 255, 0.02); border: none; border-top-left-radius: 18px; border-top-right-radius: 18px; }"
        )
        titlebar_layout = QVBoxLayout(titlebar)
        titlebar_layout.setContentsMargins(14, 8, 14, 8)
        titlebar_layout.setSpacing(0)

        dots_row = QHBoxLayout()
        dots_row.setContentsMargins(0, 0, 0, 0)
        dots_row.setSpacing(8)

        red = QLabel("●")
        red.setStyleSheet("color: #ff6b5f; font-size: 12px; background: transparent;")
        yellow = QLabel("●")
        yellow.setStyleSheet("color: #f5c76e; font-size: 12px; background: transparent;")
        green = QLabel("●")
        green.setStyleSheet("color: #67d77d; font-size: 12px; background: transparent;")

        dots_row.addWidget(red, alignment=Qt.AlignmentFlag.AlignLeft)
        dots_row.addWidget(yellow, alignment=Qt.AlignmentFlag.AlignLeft)
        dots_row.addWidget(green, alignment=Qt.AlignmentFlag.AlignLeft)
        dots_row.addStretch()

        titlebar_layout.addLayout(dots_row)
        layout.addWidget(titlebar)

        terminal_body = QWidget(self)
        terminal_body.setStyleSheet("QWidget { background: transparent; }")
        terminal_body_layout = QVBoxLayout(terminal_body)
        terminal_body_layout.setContentsMargins(20, 12, 20, 18)
        terminal_body_layout.setSpacing(4)

        terminal_text = QLabel(self.text)
        terminal_text.setWordWrap(True)
        terminal_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        terminal_text.setStyleSheet(
            "font-family: 'Menlo', 'Monaco', 'Consolas', 'Courier New', monospace; "
            "font-size: 12px; line-height: 1.6; color: #dfe7ef;"
        )
        terminal_body_layout.addWidget(terminal_text)

        layout.addWidget(terminal_body)
