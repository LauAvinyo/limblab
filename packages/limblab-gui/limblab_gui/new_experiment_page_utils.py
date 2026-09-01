import os
from PyQt6.QtWidgets import (
    QFileDialog,)

class NewExperimentPage:
    def _choose_output_parent_dir(self):
            """User picks the parent folder; the actual experiment folder
            (named after the experiment ID) gets created lazily once the
            experiment ID is known, in create_new_experiment()."""
            parent_dir = QFileDialog.getExistingDirectory(
                self,
                "Choose a location to save this experiment's files",
                os.getcwd(),
            )
            if not parent_dir:
                return
            self.experiment_storage_folder = parent_dir
            self.output_folder_label.setText(parent_dir)

#this is for teh new experiment page to refresh the last uploaded dapi and gene channels from the previous new added experiment
    def refresh_channel_status(self):
        """Call this after uploading a DAPI or gene channel to update the status label."""
        if hasattr(self, "channel_status_label"):
            self.channel_status_label.setText(self._build_channel_status_text())


    def _build_channel_status_text(self):
        """Builds a human-readable summary of what's been uploaded so far."""
        if self.uploaded_dapi_channel:
            dapi_text = self.uploaded_dapi_channel  # filename
        else:
            dapi_text = 'Please, upload a DAPI channel'

        if self.uploaded_gene_channel:
            gene_text = ', '.join(
                f"{channel_type} ({filename})"
                for channel_type, filename in self.uploaded_gene_channel.items()
            )
        else:
            gene_text = 'No gene channels were uploaded'

        return f"DAPI channel: {dapi_text}\nGene channel(s): \n{gene_text}"
