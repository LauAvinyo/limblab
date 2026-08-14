from pathlib import Path
from typing import List, Optional
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


class Channel(SQLModel, table=True):
    """Database table for dynamic image channels."""

    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: str = Field(
        foreign_key="experiment.experiment_id", ondelete="CASCADE")
    channel_name: str
    path: str
    current_state : Optional[str]
    #workflow_container: Optional[list] -> no funciona
    workflow_container_ch: Optional[list] = Field(
        default=None,
        sa_column=Column(JSON))
    
    clean_isovalue_min : Optional[float]#no es pot tupla/millor aixi!
    clean_isovalue_max : Optional[float]
    clean_path : Optional[str]

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
    species: Optional[str] = None
    workflow_container_exp: Optional[list] = Field(
            default=None,
            sa_column=Column(JSON))
    surface_path: Optional[str] = None
    surface_isovalue: Optional[int] = None
    stage: Optional[int] = None
    transformation_matrix_path: Optional[str] = None
    rotation_matrix_path : Optional[str] = None
    linear_transform: Optional[str] = None
    nonlinear_transform: Optional[str] = None

    channels: List[Channel] = Relationship(
        back_populates="experiment",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
        },
    )
