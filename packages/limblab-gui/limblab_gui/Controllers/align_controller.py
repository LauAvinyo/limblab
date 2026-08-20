# pyright: reportOptionalMemberAccess=false
# pyright: ignore[reportAttributeAccessIssue]

from limblab import _store_transformation_matrix, rotate_limb
from limblab.design import theme
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QWidget,
)
from utils import create_styled_button
from limblab.database import save_experiment


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

        # Chrome (menu bar + action bar) is built once in MainWindow.__init__.
        # Never rebuild it here — just tell the fixed bar which step is active.
        self.window._refresh_pipeline_actions(current_step="Align")

        # Start alignment viewer
            
        
        try:
            self.plotter, self.source, self.surface_path = rotate_limb(
                experiment=experiment,
                db_path = str(self.window.db_path),#the main window path for our database is a Path object, and rotate_limb takes a str argument for it!
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
        bar.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)

        confirm_btn = create_styled_button("Confirm Alignment")
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

        self.experiment.transformation_matrix_path = transformation_path
        
        save_experiment(self.window.db_path, self.experiment)

        self.window.workflow_state["align_done"] = True
        self.window.workflow_state["alignment_method"] = "rigid"  # whatever you track

        # The step is now "done" — refresh the fixed action bar so the
        # checkmark/label updates immediately without touching the menu.
        self.window._refresh_pipeline_actions(current_step="Align")

        self.window.log_pipeline(
            f"Alignment completed.\nMatrix written to:\n{self.experiment.transformation_matrix_path}"
        )
        self._go_next_from_align()


    def _go_next_from_align(self): 
        if self.experiment.transformation_matrix_path is None :
            QMessageBox.warning(
                                    self.window,
                                    "Alignment required",
                                    "Please confirm an alignment before continuing.",
                                )
            return
        else:
            print('@')
            self.window._show_message(f"Alignment was performed!\nYou can now Visualize your limb surface")
            self.window.visualizer.show(self.current_experiment)

