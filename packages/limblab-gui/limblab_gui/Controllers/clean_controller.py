from limblab import pick_isovalues, clean, get_channel_path, save_experiment
from limblab.params import CleanParams

from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QMessageBox, QWidget,
    QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox,
)
from utils import create_styled_button, create_label


class CleanController:
    def __init__(self, window):
        self.window = window
    
        self.plotter = None
        self.experiment = None
        self.channel_name = None
        self.raw_volume_path = None
        self.v0 = None
        self.v1 = None


    def show(self,experiment):
        self.experiment = experiment

        container = self.window._build_workflow_container(
            next_label="Extract Surface",
            next_callback=self._go_next_from_clean,
            back_guard=lambda: (
                self.window.workflow_state["clean_done"],
                "You haven't cleaned any volume yet.",
            ),
            action_widget=self._build_clean_action_bar(),
        )
        self.window.setCentralWidget(container)

        menu_bar = self.window._reset_top_menu_bar()
        self.window._build_file_menu(menu_bar)
        self.window._build_view_menu(menu_bar)

        # If the experiment already has a DAPI channel (e.g. loaded from DB,
        # or your test experiment), auto-select it and load it into the
        # picker right away — no need to click "Load Volume" first.
        #

        #TODO change this for any current volume cleaning, any channel. So if teh user wants to remove the surface they can
        #upload here the DAPI and proceed, if not, if htey onlly have a gene channel, its ok, they can clean volume and proeceed with
        has_dapi = any(
            ch.channel_name.upper() == "DAPI" for ch in (self.experiment.channels or [])
        )
        if has_dapi:
            self.clean_widgets["channel"].setCurrentText("DAPI")
            self._load_volume_for_picking()


    def _build_clean_action_bar(self):
        """Build the clean action bar with all CleanParams widgets."""
        bar = QWidget()
        bar.setStyleSheet("background-color: #1E1E1E;")
        layout = QVBoxLayout(bar)  # Changed to VBox for more widgets
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # Store widgets for parameter access
        self.clean_widgets = {}

        layout.addStretch(1)

        # --- Channel select + Load button ---
        channel_row = QHBoxLayout()
        channel_row.addWidget(create_label("Channel:", "color: #fff; font-weight: bold; font-size: 12px;"))

        channel_combo = QComboBox()
        channel_combo.addItems(["DAPI", "BMP2", "Sox9", "Hoxa11"])
        channel_combo.setFixedHeight(28)
        channel_row.addWidget(channel_combo)
        self.clean_widgets["channel"] = channel_combo

        iso_group = QGroupBox("Isovalue Thresholds (picked from viewer)")
        iso_group.setStyleSheet("QGroupBox { color: #A0A0A0; border: 1px solid #2A2A2A; margin-top: 8px; font-size: 11px; }")
        iso_layout = QVBoxLayout(iso_group)
        iso_layout.setSpacing(10)

        v0_row = QHBoxLayout()
        self.v0_label = create_label("Lower (v0): —", "color: #fff; font-size: 12px;")
        set_v0_btn = create_styled_button("Set Lower from Slider", "#2A2A2A", "#41B3A2")
        set_v0_btn.setStyleSheet("QPushButton { background-color: #2A2A2A; color: #ffffff; font-weight: bold; font-size: 11px; border-radius: 20px; padding: 3px 8px; } QPushButton:hover { background-color: #41B3A2; }")
        set_v0_btn.clicked.connect(self._set_v0)
        v0_row.addWidget(self.v0_label)
        v0_row.addWidget(set_v0_btn)
        v0_row.addStretch()
        iso_layout.addLayout(v0_row)

        v1_row = QHBoxLayout()
        self.v1_label = create_label("Upper (v1): —", "color: #fff; font-size: 12px;")
        set_v1_btn = create_styled_button("Set Upper from Slider", "#2A2A2A", "#41B3A2")
        set_v1_btn.setFixedHeight(26)
        set_v1_btn.setStyleSheet("QPushButton { background-color: #2A2A2A; color: #ffffff; font-weight: bold; font-size: 11px; border-radius: 20px; padding: 3px 8px; } QPushButton:hover { background-color: #41B3A2; }")
        set_v1_btn.clicked.connect(self._set_v1)
        v1_row.addWidget(self.v1_label)
        v1_row.addWidget(set_v1_btn)
        v1_row.addStretch()
        iso_layout.addLayout(v1_row)

        layout.addWidget(iso_group)

        # --- Remaining params (unchanged, just smaller spinboxes) ---
        sigma_spin = QDoubleSpinBox()
        sigma_spin.setRange(0.1, 10.0); sigma_spin.setSingleStep(0.1); sigma_spin.setValue(1.5)
        sigma_spin.setFixedHeight(26)
        self.clean_widgets["gaussian_sigma"] = sigma_spin
        sigma_row = QHBoxLayout()
        sigma_row.addWidget(create_label("Gaussian Sigma:", "color: #fff; font-size: 12px;"))
        sigma_row.addWidget(sigma_spin); sigma_row.addStretch()
        layout.addLayout(sigma_row)

        freq_spin = QDoubleSpinBox()
        freq_spin.setRange(0.01, 1.0); freq_spin.setSingleStep(0.05); freq_spin.setValue(0.3)
        freq_spin.setFixedHeight(26)
        self.clean_widgets["frequency_cutoff"] = freq_spin
        freq_row = QHBoxLayout()
        freq_row.addWidget(create_label("Frequency Cutoff:", "color: #fff; font-size: 12px;"))
        freq_row.addWidget(freq_spin); freq_row.addStretch()
        layout.addLayout(freq_row)

        res_spin = QSpinBox()
        res_spin.setRange(64, 512); res_spin.setSingleStep(16); res_spin.setValue(256)
        res_spin.setFixedHeight(26)
        self.clean_widgets["low_res_size"] = res_spin
        res_row = QHBoxLayout()
        res_row.addWidget(create_label("Low Res Size:", "color: #fff; font-size: 12px;"))
        res_row.addWidget(res_spin); res_row.addStretch()
        layout.addLayout(res_row)

        # --- Execute ---
        execute_btn = create_styled_button("Clean Volume", "#0D7C66", "#41B3A2")
        execute_btn.clicked.connect(self._execute_clean)
        btn_row = QHBoxLayout()
        btn_row.addStretch(); btn_row.addWidget(execute_btn); btn_row.addStretch()
        layout.addLayout(btn_row)

        return bar


    def _load_volume_for_picking(self):
        try:
            self.channel_name = self.clean_widgets["channel"].currentText()
            self.raw_volume_path = get_channel_path(self.experiment, self.channel_name)

            self.plotter = pick_isovalues(
                raw_volume_path=self.raw_volume_path,
                renderer="pyqt",
                outside_class=self.window,
            )
            self.v0 = self.v1 = None
            self.v0_label.setText("Lower (v0): —")
            self.v1_label.setText("Upper (v1): —")

        except Exception as e:
            QMessageBox.critical(self.window, "Load error", str(e))



    def _set_v0(self):
        if self.plotter is None:
            QMessageBox.warning(self.window, "No volume loaded", "Click 'Load Volume' first.")
            return
        self.v0 = int(self.plotter.sliders[0][0].value)
        self.v0_label.setText(f"Lower (v0): {self.v0}")

    def _set_v1(self):
        if self.plotter is None:
            QMessageBox.warning(self.window, "No volume loaded", "Click 'Load Volume' first.")
            return
        self.v1 = int(self.plotter.sliders[0][0].value)
        self.v1_label.setText(f"Upper (v1): {self.v1}")



    def _execute_clean(self):
        try:
            if self.raw_volume_path is None:
                raise RuntimeError("Load a volume (.tiff) before cleaning.")
            if self.v0 is None or self.v1 is None:
                raise RuntimeError("Pick both a lower and upper isovalue first.")
            if self.v0 == self.v1:
                raise RuntimeError("Lower and upper isovalues must differ.")

            clean_params = CleanParams(
                v0=self.v0,
                v1=self.v1,
                gaussian_sigma=self.clean_widgets["gaussian_sigma"].value(),
                frequency_cutoff=self.clean_widgets["frequency_cutoff"].value(),
                low_res_size=self.clean_widgets["low_res_size"].value(),
            )

            new_channel = clean(
                experiment=self.experiment,
                raw_volume_path=self.raw_volume_path,
                channel_name=self.channel_name,
                params=clean_params,
            )

        except Exception as e:
            QMessageBox.critical(self.window, "Clean error", str(e))
            return

        # Replace existing channel entry of the same name, or add it
        self.experiment.channels = [
            ch for ch in self.experiment.channels
            if ch.channel_name.upper() != new_channel.channel_name.upper()
        ] + [new_channel]

        save_experiment(self.window.db_path, self.experiment)

        self.window.workflow_state["clean_done"] = True
        self.window.workflow_state["last_cleaned_channel"] = new_channel.channel_name
        self.window.log_pipeline(
            f"Cleaned {new_channel.channel_name} (v0={new_channel.v0}, v1={new_channel.v1}).\n"
            f"Written to:\n{new_channel.path}"
        )


    def _go_next_from_clean(self):
        if not self.window.workflow_state["clean_done"]:
            QMessageBox.warning(
                self.window, "Clean required",
                "Please clean a channel before continuing.",
            )
            return

        if self.window.workflow_state["last_cleaned_channel"] == "DAPI":
            self.window.navigate_to(lambda: self.window.surface.show(self.window.current_experiment))
        else:
            self.window.navigate_to(self.window.show_viz)