from pathlib import Path
from models import Channel, Experiment
from database import (
    delete_experiment,
    get_experiment,
    init_db,
    list_experiments,
    save_experiment,
)

from colorama import Fore, Style

if __name__ == "__main__":
    DB_PATH = Path("experiments.db")
    if DB_PATH.exists():
        DB_PATH.unlink()

    init_db(DB_PATH)

    # 1. CREATE directly as Pydantic/SQLModel instances
    exp1 = Experiment(
        experiment_id="HCR10_SHH_l3",
        base="./HCR10_SHH_l3",
        spacing_x=0.65,
        spacing_y=0.65,
        spacing_z=2.0,
        side="L",
        position="H",
        channels=[
            Channel(experiment_id="HCR10_SHH_l3", channel_name="DAPI", path="dapi.vti", v0=238.0, v1=463.0),
            Channel(experiment_id="HCR10_SHH_l3", channel_name="SHH", path="shh.vti", v0=174.0, v1=335.0),
            Channel(experiment_id="HCR10_SHH_l3", channel_name="SOX9", path="sox9.vti", v0=392.0, v1=418.0),
        ],
    )
    save_experiment(DB_PATH, exp1)

    # 2. READ (No manual conversion needed, comes back as Pydantic model)
    retrieved = get_experiment(DB_PATH, "HCR10_SHH_l3")
    if retrieved is None:
        raise ValueError("Experiment not found")
    print(f"Loaded: {retrieved.experiment_id}, Side: {retrieved.side}")
    for ch in retrieved.channels:
        print(f" -> Channel {ch.channel_name}: {ch.path}")

    # 3. UPDATE
    retrieved.species = "Mouse"
    retrieved.channels.append(
        Channel(experiment_id="HCR10_SHH_l3", channel_name="FGF8", path="fgf8.vti", v0=100.0, v1=200.0)
    )
    save_experiment(DB_PATH, retrieved)

    # 4. DELETE
    delete_experiment(DB_PATH, "HCR10_SHH_l3")
    print(f"Remaining: {list_experiments(DB_PATH)}")

    if DB_PATH.exists():
        DB_PATH.unlink()