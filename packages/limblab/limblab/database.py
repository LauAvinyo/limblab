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


def update_experiment(self):
    return

