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
        session.merge(
            experiment
        )  # Insert or update experiment + cascade update channels
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
    #the functions to handle going back should use delete_experiment, must not go into the controllers!


#added database function for deleting specific channel .tifs
#as channel has an id we can direclty acecess the selected channel 
def delete_channel(db_path: Path, channel_id: int) -> bool:
    engine = get_engine(db_path)
    with Session(engine) as session:
        channel = session.get(Channel, channel_id)
        if channel:
            session.delete(channel)
            session.commit()
            return True
        return False


def update_experiment(
    db_path: Path, experiment_id: str, **kwargs
) -> Optional[Experiment]:
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


def rename_experiment(db_path: Path, experiment_id: str, new_name: str) -> bool:
    engine = get_engine(db_path)
    with Session(engine) as session:
        exp = session.get(Experiment, experiment_id)
        if exp:
            exp.display_name = new_name
            session.add(exp)
            session.commit()
            return True
        return False



# Keep the standalone script functionality for testing
if __name__ == "__main__":
    DB_PATH = Path("experiments.db")

    # Test reading the data
    retrieved = get_experiment(DB_PATH, "HCR10_SHH_l3")
    if retrieved:
        print(f"\n📖 Loaded: {retrieved.experiment_id}, Side: {retrieved.side}")
        for ch in retrieved.channels:
            print(f"   -> Channel {ch.channel_name}: {ch.path}")

    print(f"\n📋 All experiments: {list_experiments(DB_PATH)}")


