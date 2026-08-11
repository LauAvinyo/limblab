# pyright: reportOptionalMemberAccess=false
# pyright: ignore[reportAttributeAccessIssue]

from limblab import _store_transformation_matrix, rotate_limb
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QWidget,
)
from utils import create_styled_button


class AlignController:
    def __init__(self, window):
        self.window = window

        # Alignment session state
        self.plotter = None
        self.source = None
        self.surface_path = None

        self.experiment = None

    # -------------------------------------------------------
    # Public
    # -------------------------------------------------------

    def show(self, experiment):
        """
        Display the Align workflow screen.
        """

        self.experiment = experiment

        container = self.window._build_workflow_container(
            next_label="Visualize",
            next_callback=self._go_next_from_align,
            back_guard=lambda: (
                self.window.workflow_state["align_done"],
                "You haven't confirmed an alignment yet.",
            ),
            action_widget=self._build_align_action_bar(),
        )

        self.window.setCentralWidget(container)

        menu_bar = self.window._reset_top_menu_bar()
        self.window._build_file_menu(menu_bar)

        # Start alignment viewer
        try:
            self.plotter, self.source, self.surface_path = rotate_limb(
                experiment=experiment,
                renderer="pyqt",
                outside_class=self.window,
            )
        except Exception as e:
            QMessageBox.critical(self.window, "Alignment error", str(e))

    # -------------------------------------------------------
    # UI
    # -------------------------------------------------------

    def _build_align_action_bar(self):
        bar = QWidget()
        bar.setStyleSheet("background-color: #1E1E1E;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)

        confirm_btn = create_styled_button(
            "Confirm Alignment",
            "#2A2A2A",
            "#41B3A2",
        )
        confirm_btn.clicked.connect(self._confirm_alignment)

        layout.addStretch()
        layout.addWidget(confirm_btn)
        layout.addStretch()

        return bar

    # -------------------------------------------------------
    # Actions
    # -------------------------------------------------------

    def _confirm_alignment(self):
        """
        User accepts the current rigid alignment.
        """

        try:
            if self.source is None:
                raise RuntimeError("No alignment source available.")

            if self.surface_path is None:
                raise RuntimeError("No surface path available.")

            T = self.source.transform  # type: ignore

            transformation_path = _store_transformation_matrix(
                T,
                self.surface_path,
            )

        except Exception as e:
            QMessageBox.critical(
                self.window,
                "Alignment error",
                str(e),
            )
            return

        self.window.workflow_state["align_done"] = True

        self.window.log_pipeline(
            f"Alignment completed.\nMatrix written to:\n{transformation_path}"
        )

    def _go_next_from_align(self):
        if not self.window.workflow_state["align_done"]:
            QMessageBox.warning(
                self.window,
                "Alignment required",
                "Please confirm an alignment before continuing.",
            )
            return

        self.window.navigate_to(self.window.show_viz)
