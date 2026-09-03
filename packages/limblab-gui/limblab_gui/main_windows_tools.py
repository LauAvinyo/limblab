from limblab.design import theme
from PyQt6.QtWidgets import (QWidget,
                             QHBoxLayout,
                             QSizePolicy)

class MainWindowsTools:
    def _centered_container(self, inner_layout, max_width=900, min_width=380):
        """Wrap a layout in a widget that stays horizontally centered and
        capped at max_width, expanding vertically to fill available space.
 
        Use this for the main content block of a "page" instead of adding
        the layout straight into the central widget, so the page keeps a
        readable proportion instead of stretching edge-to-edge on large /
        fullscreen windows.
        """
        inner = QWidget()
        inner.setLayout(inner_layout)
        inner.setMinimumWidth(min_width)
        inner.setMaximumWidth(max_width)
        inner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
 
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch(1)
        wrapper_layout.addWidget(inner)
        wrapper_layout.addStretch(1)
        return wrapper
 
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_responsive_scaling()
 
    def _apply_responsive_scaling(self):
        """Rescale hero-style labels relative to the current window width.
 
        Keeps proportions consistent between a small window and a maximized
        / fullscreen one instead of the fonts staying pinned at whatever
        size they were created at. Values are clamped so text never gets
        absurdly tiny or huge.
        """
        width = self.width() or 1280
        scale = max(0.8, min(1.8, width / 1280))
 
        def _rescale(attr_name, base_size):
            widget = getattr(self, attr_name, None)
            if widget is None:
                return
            try:
                fnt = widget.font()
                fnt.setPointSize(max(10, int(base_size * scale)))
                widget.setFont(fnt)
            except RuntimeError:
                # underlying Qt widget was already destroyed (page navigated away)
                pass
 
        try:
            hero_size = int(theme("typography.fontSizeHero", 100))
        except Exception:
            hero_size = 100
        try:
            section_hero_size = int(theme("typography.fontSizeHero", 40))
        except Exception:
            section_hero_size = 40
 
        _rescale("label_main", hero_size)
        _rescale("label_upload", section_hero_size)
        _rescale("label_library", section_hero_size)
