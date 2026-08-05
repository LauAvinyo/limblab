from pathlib import Path
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class Channel(SQLModel, table=True):
    """Database table for dynamic image channels."""

    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: str = Field(foreign_key="experiment.experiment_id", ondelete="CASCADE")
    channel_name: str
    path: str
    v0: float
    v1: float

    # Relationship back to parent experiment
    experiment: Optional["Experiment"] = Relationship(back_populates="channels")


class Experiment(SQLModel, table=True):
    """Database table and Pydantic model for Experiments."""

    experiment_id: str = Field(primary_key=True)
    base: str
    spacing_x: float
    spacing_y: float
    spacing_z: float
    side: Optional[str] = None
    position: Optional[str] = None
    surface: Optional[str] = None
    species: Optional[str] = None

    channels: List[Channel] = Relationship(
            back_populates="experiment",
            sa_relationship_kwargs={
                "cascade": "all, delete-orphan",
                "lazy": "selectin",
            },
        )