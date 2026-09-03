import os
import shutil
from pathlib import Path

from limblab.database.crud import (
    delete_channel,
    delete_experiment,
    get_experiment,
    init_db,
    list_experiments,
    rename_experiment,
    save_experiment,
)
from limblab.models import Channel, Experiment
from PyQt6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMessageBox,
    
)

class DatabaseGUI:
    def addchannel_button_clicked(self, checked=False):
        """Add channel button handler - adds a channel to an existing experiment."""
        self._add_channel_to_existing()

    def _refresh_experiments(self):
        """Refresh the experiments list."""
        self._load_experiments_from_db()
        self.show_user_experiment_list()
        QMessageBox.information(self, "Refreshed", "Experiment list updated.")


    def _set_current_experiment(self, exp_obj):
        """Switch the active experiment. Pipeline progress is derived from
        what's actually saved on this experiment's row — so resuming an
        experiment you cleaned/surfaced last week correctly shows those
        steps unlocked, without needing a separate progress table."""
        
        self.experiment = exp_obj

    def _load_experiments_from_db(self):
        """Load all experiments from the database."""
        try:
            # Get list of experiment IDs from database
            exp_ids = list_experiments(self.db_path)
            self.experiments = exp_ids

            # Load metadata for each experiment
            self.experiment_metadata = {}
            self.experiment_names = {}

            for exp_id in exp_ids:
                exp_data = get_experiment(self.db_path, exp_id)
                if exp_data:
                    self.experiment_metadata[exp_id] = exp_data
                    # Use the persisted display name if set, otherwise fall back to the id
                    self.experiment_names[exp_id] = exp_data.displayed_name or exp_id

            print(f"Loaded {len(self.experiments)} experiments from database")

        except Exception as e:
            
            self.experiments = []
            self.experiment_metadata = {}


    def _rename_experiment(self, path, experiment_id, old_name):
        """Rename an experiment and persist to DB."""

        experiment = get_experiment(self.db_path, experiment_id)

        current_name = old_name #exp_id as default in models.py
        new_name, ok = QInputDialog.getText(
            self, "Rename experiment", "New name:", text=current_name
        )
        if ok and new_name.strip():
            success = rename_experiment(self.db_path, experiment_id, new_name.strip())
            if success:
                self.experiment_names[path] = new_name.strip()#internal main window variable to store the current experiments loaded
                experiment.displayed_name = new_name
                self.show_user_experiment_list()
            else:
                QMessageBox.warning(self, "Error", f"Experiment '{path}' not found in database.")

    # DELETE FUNCTION CALLS DATABASE DELETE FUNCTION, AUXILIAR UI
    def _delete_experiment(self, experiment_id, displayed_name):
        """Delete an experiment from the database and its output folder on disk."""
        # Grab the folder location before we remove the DB row (cascades to channels)
        exp_data = self.experiment_metadata.get(experiment_id)
        exp_base = getattr(exp_data, "base", None) if exp_data else None

        # Confirm with user
        folder_note = f"\n\nFolder to be removed:\n{exp_base}" if exp_base else ""
        reply = QMessageBox.question(
            self,
            "Delete Experiment",
            f"Are you sure you want to delete experiment '{displayed_name}'?\n"
            f"This will permanently delete all its associated channels from the database "
            f"and delete the entire generated output folder for this experiment.{folder_note}\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:

            success = delete_experiment(self.db_path, experiment_id)#delete_experiment as a functioin imported from database.py

            if success:#delete function returns True if exp ( exp = session.get(Experiment, experiment_id, if exp: session.delete(exp)session.commit() return True
                # Remove the experiment's output folder from disk (best-effort)
                if exp_base:
                    self._delete_folder(exp_base)

                # Remove from local lists (UI logistics)
                if experiment_id in self.experiments:
                    self.experiments.remove(experiment_id)
                if experiment_id in self.experiment_names:
                    del self.experiment_names[experiment_id]
                if experiment_id in self.experiment_metadata:
                    del self.experiment_metadata[experiment_id]

                # Refresh the UI
                self.show_user_experiment_list()
                QMessageBox.information(
                    self, "Success", f"Deleted experiment: {displayed_name}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Experiment '{displayed_name}' not found in database.",
                )


    def _delete_channel(self, experiment_id, channel_name, channel_id):
        """Delete a channel from an experiment, its DB entry, and the files
        generated from it in the experiment's output folder."""
        exp_data = self.experiment_metadata.get(experiment_id)
        exp_base = getattr(exp_data, "base", None) if exp_data else None

        # Find the channel's own record so we know its originally uploaded
        # filename (used below to make sure that raw file is removed too).
        channel_path = None
        if exp_data:
            for ch in (exp_data.channels or []):
                if getattr(ch, "id", None) == channel_id:
                    channel_path = getattr(ch, "path", None)
                    break

        reply = QMessageBox.question(
            self,
            "Delete Channel",
            f"Are you sure you want to delete the selected channel '{channel_name}' from experiment '{experiment_id}'?\n"
            f"This will permanently delete the channel's database entry and all files generated "
            f"from this channel (the uploaded volume and any derived outputs) in the experiment's output folder.\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = delete_channel(self.db_path, channel_id)

            if success:
                if exp_base:
                    self._delete_channel_files(exp_base, channel_name, channel_path)

                self._load_experiments_from_db()
                self.show_user_experiment_list()
                QMessageBox.information(
                    self, "Success", f"Deleted channel: {channel_name}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Channel '{channel_name}' not found in database.",
                )

    def _delete_folder(self, folder_path):
        """Best-effort removal of an experiment's output folder from disk."""
        try:
            if folder_path and os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Cleanup warning",
                f"The database entry was deleted, but the output folder couldn't be "
                f"removed automatically:\n{folder_path}\n\n{e}\n\nYou may need to delete it manually.",
            )

    def _delete_channel_files(self, exp_base, channel_name, channel_path=None):
        """Best-effort removal of the files generated for a specific channel
        from the experiment's output folder.
        assumes generated/derived files are named containing the
        channel name (e.g. produced by the pipeline steps for that channel).
        The originally uploaded volume is removed via its exact stored path
        regardless of naming, since it may not contain the channel name.
        """
        try:
            base = Path(exp_base)
            if not base.is_dir():
                return

            removed_any = False

            # 1) Remove the exact originally-uploaded file for this channel.
            if channel_path:
                raw_file = base / channel_path
                if raw_file.is_file():
                    raw_file.unlink()
                    removed_any = True

            # 2) Remove any other file whose name references this channel
            #    (derived/generated outputs from the pipeline).
            for f in base.iterdir():
                if not f.is_file() or f.name == "database.db":
                    continue
                if channel_name.lower() in f.name.lower():
                    f.unlink()
                    removed_any = True

            if not removed_any:
                print(f"No files matching channel '{channel_name}' found in {exp_base}")

        except Exception as e:
            QMessageBox.warning(
                self,
                "Cleanup warning",
                f"The channel's database entry was deleted, but some of its generated "
                f"files couldn't be removed automatically from:\n{exp_base}\n\n{e}",
            )


    def create_new_experiment(self, channel_type: str):
        """Create a new experiment from any TIF volume (DAPI or gene channel)."""
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select TIF volume file!',
            directory=os.getcwd(),
            filter='Volume files (*.tif *.tiff *.vti *.nii *.nii.gz)'
        )
        if not filepath:
            return

        if not filepath.lower().endswith((".tif", ".tiff", ".vti", ".nii", ".nii.gz")):
            QMessageBox.warning(self, "Invalid file", "Please select a valid volume file.")
            return

        exp_id = os.path.basename(filepath).split('.')[0]
        filename = os.path.basename(filepath)

        if channel_type == 'DAPI':
        # Starting a brand-new experiment. Everything uploaded afterwards
        # on this page (gene channels) attaches to THIS experiment —
        # it never gets its own exp_id from its own filename.
            exp_id = filename.split('.')[0]

            if exp_id in self.experiments:
                reply = QMessageBox.question(
                self, "Experiment Exists",
                f"Experiment '{exp_id}' already exists.\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                    
            if not self.experiment_storage_folder:
                            QMessageBox.warning(
                                self, "Choose an output folder first",
                                "Please choose where to save this experiment's files before uploading a channel."
                            )
                            return

            output_dir = os.path.join(self.experiment_storage_folder, exp_id)
            os.makedirs(output_dir, exist_ok=True)
            dest_path = os.path.join(output_dir, filename)
            shutil.copy2(filepath, dest_path)

            new_exp = Experiment(
                experiment_id=exp_id,
                displayed_name=exp_id,
                base=output_dir,
                spacing_x=self.limb_info['spacing'][0],
                spacing_y=self.limb_info['spacing'][1],
                spacing_z=self.limb_info['spacing'][2],
                side=self.limb_info['side'],
                position=self.limb_info['position'],
                channels=[],
            )
            self.experiment = new_exp
            save_experiment(self.db_path, new_exp)

            channel_name = 'DAPI'


        else:
            # Attach a gene channel to the experiment already started on this
            # page. Never mint a new experiment_id from the gene file's name.
            if self.experiment is None or not self.uploaded_dapi_channel:
                QMessageBox.warning(
                    self, "Upload DAPI first",
                    "Please upload a DAPI channel before adding a gene channel."
                )
                return

            channel_name, ok = QInputDialog.getItem(
                self, "Channel Type", "Select the channel type for this file:",
                self.GENE_CHANNEL_TYPES, 0, False
            )
            if not ok or not channel_name:
                return

            if any(ch.channel_name.upper() == channel_name.upper() for ch in self.experiment.channels):
                QMessageBox.warning(
                    self, "Duplicate Channel",
                    f"Channel '{channel_name}' has already been uploaded for this experiment."
                )
                return

            # Copy into the SAME experiment folder the DAPI channel lives in.
            dest_path = os.path.join(self.experiment.base, filename)
            shutil.copy2(filepath, dest_path)

        new_channel = Channel(
            experiment_id=self.experiment.experiment_id,
            channel_name=channel_name,
            path=filename,
        )
        self.experiment.channels.append(new_channel)
        save_experiment(self.db_path, self.experiment)
        self._sync_db_copy(self.experiment.base)

        if channel_type == 'DAPI':
            self.uploaded_dapi_channel = filename
        else:
            self.uploaded_gene_channel[channel_name] = filename


        if self.experiment_storage_folder == None:
            QMessageBox('Select directory for output folder', 'Please select an output directory for the output folder to be generated')

        self.refresh_channel_status()
        self._load_experiments_from_db()
        return

    def _add_channel_to_existing(self, specific_exp_id=None):
        if not specific_exp_id:
            if not self.experiments:
                QMessageBox.warning(self, "No experiments", "No existing experiments found.")
                return
            exp_id, ok = QInputDialog.getItem(
                self, "Select Experiment", "Select experiment to add channel to:",
                self.experiments, 0, False
            )
            if not ok or not exp_id:
                return
        else:
            exp_id = specific_exp_id

        exp_data = self.experiment_metadata.get(exp_id)
        if not exp_data:
            QMessageBox.warning(self, "Error", "Experiment not found.")
            return

        current_channels = [ch.channel_name for ch in (exp_data.channels or [])]
        channel_info = f"Current channels: {', '.join(current_channels) if current_channels else 'None'}"

        filepath, _ = QFileDialog.getOpenFileName(
            parent=self, caption='Select gene channel TIF file!',
            directory=os.getcwd(),
            filter='Volume files (*.tif *.tiff *.vti *.nii *.nii.gz)'
        )
        if not filepath:
            return
        if not filepath.lower().endswith((".tif", ".tiff", ".vti", ".nii", ".nii.gz")):
            QMessageBox.warning(self, "Invalid file", "Please select a valid volume file.")
            return

        channel_type, ok = QInputDialog.getItem(
            self, "Channel Type", f"Select channel type to add:\n\n{channel_info}",
            ['DAPI',"HOXA11", 'HOXA13', "SOX9", 'AFF3',"BMP2", "SHH"], 0, False
        )
        if not ok or not channel_type:
            return

        try:
            for channel in exp_data.channels or []:
                if channel.channel_name.upper() == channel_type.upper():
                    QMessageBox.warning(
                        self, "Duplicate Channel",
                        f"Channel '{channel_type}' already exists in this experiment.\n{channel_info}"
                    )
                    return

            dest_path = os.path.join(exp_data.base, os.path.basename(filepath))
            shutil.copy2(filepath, dest_path)

            new_channel = Channel(
                experiment_id=exp_id,
                channel_name=channel_type,
                path=os.path.basename(filepath),
            )

            exp_data.channels.append(new_channel)
            save_experiment(self.db_path, exp_data)
            self._sync_db_copy(exp_data.base) # exp_data is already a real Experiment — no need to rebuild it

            self._load_experiments_from_db()

            is_valid, status = self._validate_experiment_channels(exp_id)
            channel_list = ', '.join(ch.channel_name for ch in exp_data.channels)

            if is_valid:
                QMessageBox.information(
                    self, "Success",
                    f"Added {channel_type} channel to experiment: {exp_id}\n"
                    f"File: {os.path.basename(filepath)}\n\n"
                  
                )
            else:
                QMessageBox.information(
                    self, "Success",
                    f"Added {channel_type} channel to experiment: {exp_id}\n"
                    f"File: {os.path.basename(filepath)}\n\n"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add channel: {e}")
            import traceback
            traceback.print_exc()


    def _sync_db_copy(self, output_dir):
        """Keep a snapshot of the shared experiments.db inside the
        experiment's own output folder, so the folder is self-contained."""
        try:
            shutil.copy2(self.db_path, os.path.join(output_dir, "database.db"))
        except Exception as e:
            print(f"Warning: couldn't copy database.db into {output_dir}: {e}")


    def _validate_experiment_channels(self, exp_id):
        exp_data = self.experiment_metadata.get(exp_id)
        if not exp_data: 
            return False, f"Experiment '{exp_id}' not found in database."

        channels = exp_data.channels or []
        if not channels:
            return False, "No channels found in this experiment.\nPlease upload at least DAPI and one gene channel."

        has_dapi = False
        gene_channels = []
        gene_names = ['HOXA11', 'HOXA13','SOX9', 'BMP2', 'SHH']

        for channel in channels:
            channel_name = channel.channel_name.upper()
            if channel_name == 'DAPI':
                has_dapi = True
            elif channel_name in [g.upper() for g in gene_names]:
                gene_channels.append(channel.channel_name)

        if not has_dapi:
            return False, "Missing required DAPI channel.\n\nPlease upload a DAPI .tiff file first."
        if len(gene_channels) == 0:
            return False, "Missing gene channels.\n\nPlease upload at least one gene channel:\n- HOXA11 \n- HOXA13\n- Sox9\n- BMP2"

        return True, f"Experiment has DAPI and {len(gene_channels)} gene channel(s): {', '.join(gene_channels)}"