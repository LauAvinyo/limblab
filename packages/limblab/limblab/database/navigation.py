import limblab
import re
from limblab.models import Experiment
from .crud import save_experiment
import sqlite3
from pathlib import Path

DATABASE_EXPERIMENT_ACTION = {
    'Clean': ['clean_path', 'clean_isovalue_min', 'clean_isovalue_max'],
    'Surface': ['surface_path', 'surface_isovalue'],
    'Stage': ['stage'],
    'Align': ['transformation_matrix_path', 'linear_transform', 'nonlinear_transform'],
}

REFERENCE_LIMBS_DIR = Path(limblab.__file__).parent / "limb"

def delete_from_database_going_back_action(db_path,experiment: Experiment,channel_name: str, action_undone: list,):
    channel = next(
        (ch for ch in experiment.channels if ch.channel_name == channel_name),
        None,
    )#current channel name in the experiment

    #this is just to inform the user through the pipeline in the right panel
    channel_cleared = []
    experiment_cleared = []

    for action in action_undone:
        fields = DATABASE_EXPERIMENT_ACTION[action]

        if action == 'Clean':#only clean has a channel specific generated argumetns
            if channel is None:
                continue#nothing happens
            for field in fields:
                if hasattr(channel, field):
                    channel_cleared.append(field)
                    setattr(channel, field, None)
        else:
            for field in fields:
                if hasattr(experiment, field):
                    experiment_cleared.append(field)
                    setattr(experiment, field, None)

    save_experiment(db_path, experiment)
    return channel, channel_cleared, experiment_cleared


def seed_reference_limbs(db_path: Path, reference_folder = REFERENCE_LIMBS_DIR) -> None:
    """Ensures reference_limbs exists and reflects what's currently on disk
    in `reference_folder`. Safe to call on every launch — re-syncs rather
    than duplicates."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reference_limbs (
                stage INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL
            )
            """
        )#cr4eates table for reference_limbs!

        found = {}
        for f in reference_folder.iterdir():
            if not f.is_file():
                continue
            #for rotate_limb we need to fetch the closest reference limb for our obtained staging integer
            m = re.match(r"Limb-rec_(\d+)$", f.stem)
            if not m:
                continue
            stage = int(m.group(1))
            found[stage] = str(f.resolve())

        conn.executemany(
            "INSERT OR REPLACE INTO reference_limbs (stage, file_path) VALUES (?, ?)",
            list(found.items()),
        )
        conn.commit()