from pathlib import Path
from typing import List, Optional
from sqlmodel import Session, SQLModel, create_engine, select
from limblab.models import Channel, Experiment


def get_engine(db_path: Path):
    """Returns an engine with foreign keys enabled."""
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(db_path: Path) -> None:
    """Creates tables automatically from SQLModel class definitions."""
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)


def save_experiment(db_path: Path, experiment: Experiment) -> None:
    """CREATE / UPDATE: Saves the model and all associated child channels directly."""
    engine = get_engine(db_path)
    with Session(engine) as session:
        session.merge(experiment)  # Insert or update experiment + cascade update channels
        session.commit()


def get_experiment(db_path: Path, experiment_id: str) -> Optional[Experiment]:
    """READ (GET): Fetches experiment. Channels are automatically loaded as Pydantic objects."""
    engine = get_engine(db_path)
    with Session(engine) as session:
        return session.get(Experiment, experiment_id)


def list_experiments(db_path: Path) -> List[str]:
    """READ (LIST): Returns all experiment IDs."""
    engine = get_engine(db_path)
    with Session(engine) as session:
        statement = select(Experiment.experiment_id)
        return list(session.exec(statement).all())


def delete_experiment(db_path: Path, experiment_id: str) -> bool:
    """DELETE: Removes experiment and automatically cascades deletion to channels."""
    engine = get_engine(db_path)
    with Session(engine) as session:
        exp = session.get(Experiment, experiment_id)
        if exp:
            session.delete(exp)
            session.commit()
            return True
        return False


def create_test_database(db_path: Path, force: bool = False) -> None:
    """Create test database with sample experiments."""

    #just for TESTING!

# 🔥 CHANGE THIS - Always delete and recreate if force=True
    if force and db_path.exists():
        db_path.unlink()
        print(f"🗑️ Removed existing database: {db_path}")
    
    # 🔥 CHANGE THIS - Don't check for existing data if force=True
    if not force and db_path.exists():
        try:
            existing = list_experiments(db_path)
            if existing:
                print(f"📂 Database already has {len(existing)} experiments: {existing}")
                print("   Use force=True to regenerate.")
                return
        except:
            db_path.unlink()

    
    # Initialize database
    init_db(db_path)

    # 1. CREATE test experiments
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
    save_experiment(db_path, exp1)

    exp2 = Experiment(
        experiment_id="HCR10_FGF_l3",
        base="./HCR10_FGF_l3",
        spacing_x=0.65,
        spacing_y=0.65,
        spacing_z=2.0,
        side="R",
        position="F",
        channels=[
            Channel(experiment_id="HCR10_FGF_l3", channel_name="DAPI", path="dapi.vti", v0=238.0, v1=463.0),
            Channel(experiment_id="HCR10_FGF_l3", channel_name="FGF8", path="fgf8.vti", v0=100.0, v1=200.0),
        ],
    )
    save_experiment(db_path, exp2)

    print(f"✅ Created test database at: {db_path}")
    print(f"   Experiments: {exp1.experiment_id}, {exp2.experiment_id}")

# Keep the standalone script functionality for testing
if __name__ == "__main__":
    DB_PATH = Path("experiments.db")
    create_test_database(DB_PATH, force=True)
    
    # Test reading the data
    retrieved = get_experiment(DB_PATH, "HCR10_SHH_l3")
    if retrieved:
        print(f"\n📖 Loaded: {retrieved.experiment_id}, Side: {retrieved.side}")
        for ch in retrieved.channels:
            print(f"   -> Channel {ch.channel_name}: {ch.path}")
    
    print(f"\n📋 All experiments: {list_experiments(DB_PATH)}")


def update_experiment(db_path: Path, experiment_id: str, **kwargs) -> Optional[Experiment]:
    """UPDATE: Update specific fields of an experiment."""
    engine = get_engine(db_path)
    with Session(engine) as session:
        exp = session.get(Experiment, experiment_id)
        if exp:
            for key, value in kwargs.items():
                if hasattr(exp, key):
                    setattr(exp, key, value)
            session.commit()
            session.refresh(exp)
            return exp
        return None

