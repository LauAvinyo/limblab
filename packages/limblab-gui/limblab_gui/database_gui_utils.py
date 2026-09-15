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

    def _open_experiment_details(self, experiment_id):
        """Show the experiment's current details (output directory, limb
        side, position, spacing) and walk the user through a quick series of
        popups to change any of them. Mirrors the values collected up-front
        on the New Experiment page, but editable after the fact. Anything
        changed is persisted back to the database."""
        exp_data = self.experiment_metadata.get(experiment_id)
        if not exp_data:
            QMessageBox.warning(self, "Error", f"Experiment '{experiment_id}' not found in database.")
            return

        # ---- Show current info, ask whether to edit ----
        current_info = (
            f"Output Directory:\n{exp_data.base or 'Not set'}\n\n"
            f"Limb Side: {exp_data.side or 'N/A'}\n"
            f"Position: {exp_data.position or 'N/A'}\n"
            f"Spacing (X, Y, Z): {exp_data.spacing_x}, {exp_data.spacing_y}, {exp_data.spacing_z}"
        )
        reply = QMessageBox.question(
            self, f"Details \u2014 {exp_data.displayed_name or experiment_id}",
            current_info + "\n\nWould you like to edit these details?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # ---- Output directory ----
        new_base = exp_data.base
        change_dir = QMessageBox.question(
            self, "Output Directory",
            f"Current output directory:\n{exp_data.base or 'Not set'}\n\nChange it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if change_dir == QMessageBox.StandardButton.Yes:
            chosen_parent = QFileDialog.getExistingDirectory(
                self, "Choose a new parent folder for this experiment", os.getcwd()
            )
            if chosen_parent:
                new_base = os.path.join(chosen_parent, experiment_id)

        # ---- Limb side ----
        side, ok = QInputDialog.getItem(
            self, "Limb Side", "Select limb side:", ["L", "R"],
            ["L", "R"].index(exp_data.side) if exp_data.side in ("L", "R") else 0, False
        )
        if not ok:
            return

        # ---- Position ----
        position, ok = QInputDialog.getItem(
            self, "Position", "Select limb position:", ["F", "H"],
            ["F", "H"].index(exp_data.position) if exp_data.position in ("F", "H") else 0, False
        )
        if not ok:
            return

        # ---- Spacing ----
        spacing_x, ok = QInputDialog.getDouble(
            self, "Spacing X", "X spacing:", exp_data.spacing_x or 0.65, 0.01, 10.0, 2
        )
        if not ok:
            return
        spacing_y, ok = QInputDialog.getDouble(
            self, "Spacing Y", "Y spacing:", exp_data.spacing_y or 0.65, 0.01, 10.0, 2
        )
        if not ok:
            return
        spacing_z, ok = QInputDialog.getDouble(
            self, "Spacing Z", "Z spacing:", exp_data.spacing_z or 2.0, 0.01, 10.0, 2
        )
        if not ok:
            return

        # ---- Persist ----
        old_base = exp_data.base
        if new_base and new_base != old_base:
            # Physically move the experiment's folder so the channel files
            # inside it (referenced by relative filename) keep resolving
            # correctly after the directory change.
            try:
                if old_base and os.path.isdir(old_base):
                    os.makedirs(os.path.dirname(new_base), exist_ok=True)
                    shutil.move(old_base, new_base)
                else:
                    os.makedirs(new_base, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not move experiment folder:\n{e}")
                return
            exp_data.base = new_base

        exp_data.side = side
        exp_data.position = position
        exp_data.spacing_x = spacing_x
        exp_data.spacing_y = spacing_y
        exp_data.spacing_z = spacing_z

        try:
            save_experiment(self.db_path, exp_data)
            if exp_data.base and os.path.isdir(exp_data.base):
                self._sync_db_copy(exp_data.base)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save changes:\n{e}")
            return

        self._load_experiments_from_db()
        self.show_user_experiment_list()
        QMessageBox.information(self, "Success", "Experiment details updated.")

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

    def _make_unique_experiment_id(self, base_exp_id):
        """Return an experiment id that isn't already used in the DB, appending
        ' (1)', ' (2)', etc. to base_exp_id until a free one is found."""
        candidate = base_exp_id
        counter = 1
        while candidate in self.experiments:
            candidate = f"{base_exp_id} ({counter})"
            counter += 1
        return candidate


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
            exp_id = filename.split('.')[0]

            # Need the output folder up-front now, since it's part of the
            # determinant for whether this is a real collision (same id AND same
            # folder) or just a name reuse in a different location.
            if not self.experiment_storage_folder:
                QMessageBox.warning(
                    self, "Choose an output folder first",
                    "Please choose where to save this experiment's files before uploading a channel."
                )
                return

            candidate_output_dir = os.path.join(self.experiment_storage_folder, exp_id)

            existing_exp_data = self.experiment_metadata.get(exp_id) if exp_id in self.experiments else None
            same_folder = bool(
                existing_exp_data and existing_exp_data.base
                and os.path.normpath(existing_exp_data.base) == os.path.normpath(candidate_output_dir)
            )

            if existing_exp_data and same_folder:
                # True match: same id AND same output folder -> this genuinely is
                # the same experiment on disk. Let the user overwrite it in place,
                # duplicate it as a new sibling experiment, or cancel.
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Experiment Exists")
                msg_box.setText(
                    f"Experiment '{exp_id}' already exists in this output folder.\n\n"
                    f"Overwrite the existing experiment, or create a duplicate copy?"
                )
                overwrite_btn = msg_box.addButton("Overwrite", QMessageBox.ButtonRole.DestructiveRole)
                duplicate_btn = msg_box.addButton("Duplicate", QMessageBox.ButtonRole.ActionRole)
                msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                msg_box.exec()

                clicked = msg_box.clickedButton()
                if clicked == duplicate_btn:
                    exp_id = self._make_unique_experiment_id(exp_id)
                    candidate_output_dir = os.path.join(self.experiment_storage_folder, exp_id)
                elif clicked != overwrite_btn:
                    return  # Cancel

            elif existing_exp_data and not same_folder:
                # Same id, but pointing at a different output folder -> not a real
                # collision on disk, just a reused name. Warn, then keep going
                # under a disambiguated id instead of blocking creation.
                original_exp_id = exp_id
                exp_id = self._make_unique_experiment_id(exp_id)
                candidate_output_dir = os.path.join(self.experiment_storage_folder, exp_id)
                QMessageBox.information(
                    self, "Name Already Used",
                    f"An experiment named '{original_exp_id}' already exists in a different "
                    f"output folder.\nThis new experiment will be saved as '{exp_id}' so it "
                    f"doesn't conflict with it."
                )

            output_dir = candidate_output_dir
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

            existing_channel = next(
                (ch for ch in self.experiment.channels if ch.channel_name.upper() == channel_name.upper()),
                None,
            )

            if existing_channel:
                reply = QMessageBox.question(
                    self, "Channel Exists",
                    f"Channel '{channel_name}' has already been uploaded for this experiment.\nOverwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if reply != QMessageBox.StandardButton.Yes:
                    return

                # If the old file on disk has a different name than the one
                # being uploaded now, remove it so it doesn't linger orphaned.
                old_path = getattr(existing_channel, "path", None)
                if old_path and old_path != filename:
                    old_file = os.path.join(self.experiment.base, old_path)
                    if os.path.isfile(old_file):
                        os.remove(old_file)

                # Drop the old DB-side entry so the new one replaces it
                # instead of sitting alongside it as a duplicate.
                self.experiment.channels.remove(existing_channel)
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
            ['DAPI',"HOXA11", 'HOXA13', "SOX9", 'AFF3',"BMP2", 'BMP4', 'BMPR1A','BMPR1B'], 0, False
        )
        if not ok or not channel_type:
            return

        try:
            existing_channel = next(
                (ch for ch in (exp_data.channels or []) if ch.channel_name.upper() == channel_type.upper()),None,
            )
            if existing_channel:
                reply = QMessageBox.question(self, "Channel type already exists",
                f"Channel: '{channel_type}' is already in this experiment.\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if reply != QMessageBox.StandardButton.Yes:
                    return

                # If the old file on disk has a different name than the one
                # being uploaded now, remove it so it doesn't linger orphaned.
                old_path = getattr(existing_channel, "path", None)
                new_filename = os.path.basename(filepath)
                if old_path and old_path != new_filename:
                    old_file = os.path.join(exp_data.base, old_path)
                    if os.path.isfile(old_file):
                        os.remove(old_file)
                # Drop the old DB-side entry so the new one replaces it
                # instead of sitting alongside it as a duplicate.
                exp_data.channels.remove(existing_channel)

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
        gene_names = ['HOXA11', 'HOXA13','SOX9', 'BMP2', 'BMP4','BMPR1A','BMPR1B']

        for channel in channels:
            channel_name = channel.channel_name.upper()
            if channel_name == 'DAPI':
                has_dapi = True
            elif channel_name in [g.upper() for g in gene_names]:
                gene_channels.append(channel.channel_name)

        if not has_dapi:
            return False, "Missing required DAPI channel.\n\nPlease upload a DAPI .tiff file first."
        if len(gene_channels) == 0:
            return False, 'Missing gene channels.\n\nPlease upload at least one gene channel:\n- HOXA11 \n- HOXA13\n- Sox9\n- BMP2\n- BMPR1A\n- BMPR1B'

        return True, f"Experiment has DAPI and {len(gene_channels)} gene channel(s): {', '.join(gene_channels)}"