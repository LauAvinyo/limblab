from limblab.database.crud import (
    get_experiment,
)

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMessageBox,
)

class VisualizationPage:
    def _view_experiment(self, experiment_id):
        """View the selected experiment (show visualization)."""
        experiment = get_experiment(self.db_path, experiment_id)
        if not experiment:
            QMessageBox.warning(self, "Error", "Experiment not found.")
            return

        channel_names = [channel.channel_name for channel in experiment.channels]

        if 'DAPI' not in channel_names:
            QMessageBox.warning(
                self, "Error",
                "DAPI-nuclei channel not found. Unable to visualize any surface. "
                "You must upload a DAPI-nuclei channel for any experiment"
            )
            return

        self._set_current_experiment(experiment)
        self.navigation.navigate_to(lambda: self.visualizer.show_experiment(self.experiment))

    def _infer_workflow_state(self, exp):
        """Derive pipeline progress from what's actually persisted on the
        experiment row + its channels, rather than trusting an in-memory flag
        that could drift from what's really on disk/DB."""
        channels = exp.channels or []

        # A channel counts as "cleaned" if its stored path is a processed .vti,
        # matching the same convention surface_controller already checks.
        cleaned_channels = [ch for ch in channels if ch.path.lower().endswith(".vti")]
        #clean_done = len(cleaned_channels) > 0
        
        last_cleaned_channel = cleaned_channels[-1].channel_name if cleaned_channels else None

        return {
            "clean_done": bool(last_cleaned_channel) , #clean_done (bool)
            "last_cleaned_channel": last_cleaned_channel,
            "surface_done": bool(exp.surface_path),
            "stage_done": bool(exp.stage),
            #"selected_stage": exp.stage,
            "align_done": bool(exp.transformation_matrix_path),
            #"alignment_method": "rigid" if exp.transformation_matrix_path else None,
        }
    

    DAPI_ONLY_STEPS = {"Surface", "Stage", "Align"}

    DAPI_STEP_CONTROLLERS = {
            "Surface": lambda self: self.surface,
            "Stage": lambda self: self.stage,
            "Align": lambda self: self.align,
        }

    def _set_processing_channel(self, exp_id, channel):
        for (e, name), cb in self._viz_channel_checkboxes.items():
            if (e, name) != (exp_id, channel.channel_name) and cb.isChecked():
                cb.blockSignals(True)
                cb.setChecked(False)
                cb.blockSignals(False)

        checkbox = self._viz_channel_checkboxes.get((exp_id, channel.channel_name))
        if checkbox is not None:
            checkbox.blockSignals(True)
            checkbox.setChecked(True)
            checkbox.blockSignals(False)

        # Move the "processing" indicator to the active channel's row
        for key, label in getattr(self, "_viz_channel_processing_labels", {}).items():
            label.setVisible(key == (exp_id, channel.channel_name))

        self.current_channel = channel.channel_name


    def _on_channel_selected(self, exp_id, channel, checked):
        current_step = getattr(self.navigation, "_current_step", None)
        is_dapi = channel.channel_name.upper() == "DAPI"

        if current_step in self.DAPI_ONLY_STEPS and not is_dapi:
            self._warn_step_requires_dapi(current_step, exp_id, channel)
            dapi = next((c for c in self.experiment.channels
                        if c.channel_name.upper() == "DAPI"), None)
            if current_step == "Surface":
                if dapi and getattr(dapi, "clean_path", None):
                    self.surface.show(self.experiment)
            elif current_step == "Stage":
                if self.experiment.surface_path:
                    self.stage.show(self.experiment)
            elif current_step == "Align":
                if self.experiment.surface_path:
                    self.align.show(self.experiment)
            return
        
        if current_step == "Clean":
            if not checked:
                self._revert_checkbox(exp_id, channel)
                return
            self._set_processing_channel(exp_id, channel)
            self.clean.show(self.experiment, channel)
            return

        if current_step != "Visualize":
            return

        if is_dapi:
            if checked:
                self.current_channel = channel.channel_name
            return
              # DAPI's actor is already shown by show_experiment; nothing to toggle here

        ready, message = self.visualizer.channel_readiness(self.experiment, channel)
        if checked and not ready:
            self._warn_gene_channel_needs_cleaning(exp_id, channel)
            return#a gene channel has been selected, so we get a warning!

        if checked:
            actor = self.visualizer._build_channel_actor(channel)
            if actor is not None:
                self.visualizer.plt.add(actor)
                self.visualizer._channel_actors[(exp_id, channel.channel_name)] = actor
                self.visualizer.plt.render()
        else:
            actor = self.visualizer._channel_actors.pop((exp_id, channel.channel_name), None)
            if actor is not None:
                self.visualizer.plt.remove(actor)
                self.visualizer.plt.render()


    def _warn_step_requires_dapi(self, current_step, exp_id, channel):
        QMessageBox.warning(
            self,
            "DAPI channel required",
            f"'{current_step}' can only be performed on the DAPI channel.\n"
            f"'{channel.channel_name}' will not be used for this step."
        )
        self._revert_checkbox(exp_id, channel)

    def _warn_gene_channel_needs_cleaning(self, exp_id, channel):
        if channel.channel_name != 'DAPI':
            self._revert_checkbox(exp_id, channel)

            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle("Channel not cleaned")

            
            box.setText(
                f"'{channel.channel_name}' hasn't been cleaned yet.\n"
                "It needs to be cleaned before it can be visualized."
            )
            clean_btn = box.addButton("Clean now", QMessageBox.ButtonRole.AcceptRole)
            box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            box.exec()

            if box.clickedButton() == clean_btn:
                self.current_channel = channel.channel_name
                self.navigation.navigate_to(lambda: self.clean.show(self.experiment, channel))


    def _revert_checkbox(self, exp_id, channel):
        checkbox = self._viz_channel_checkboxes.get((exp_id, channel.channel_name))
        if checkbox is not None:
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)

    def viewexp_button_clicked(self):
        """View experiment button handler."""
        # Use the experiments tree selection to determine the experiment to view
        if not hasattr(self, 'experiments_tree') or self.experiments_tree.currentItem() is None:
            QMessageBox.warning(self, "No experiment selected", "Please select an experiment to visualize.")
            return

        item = self.experiments_tree.currentItem()
        parent = item.parent() if item.parent() is not None else item
        exp_id = parent.data(0, Qt.ItemDataRole.UserRole)
        if not exp_id:
            QMessageBox.warning(self, "No experiment selected", "Please select an experiment to visualize.")

            return

        exp_obj = get_experiment(self.db_path, exp_id)
        if not exp_obj:
            QMessageBox.warning(self, "Not found", f"Experiment '{exp_id}' not found in database.")
            return

        self._set_current_experiment(exp_obj)
        self._hide_busy()


    def log_pipeline(self, message):
        """Add a message to the pipeline log."""
        self.pipeline_log.append(message)
        if hasattr(self, "pipeline_log_widget"):
            self.pipeline_log_widget.setText("\n".join(self.pipeline_log[-10:]))
