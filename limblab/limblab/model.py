from pathlib import Path
from typing import Dict, Literal, Optional, Tuple
from pydantic import BaseModel, Field


class ChannelConfig(BaseModel):
    path: Path
    v0: float
    v1: float


class PipelineConfig(BaseModel):
    base: Path
    spacing: Tuple[float, float, float]
    nuclei: ChannelConfig
    channels: Dict[str, ChannelConfig] = Field(default_factory=dict)

    side: Optional[Literal["L", "R"]] = None
    position: Optional[str] = None
    surface: Optional[Path] = None
    species: Optional[str] = None

    @classmethod
    def load(cls, path: Path) -> "PipelineConfig":
        """Loads a config file from disk."""
        return cls.from_config_text(path.read_text())

    def save(self, path: Path) -> None:
        """Saves the config model back to disk in custom key-value format."""
        path.write_text(self.to_config_text())

    def to_config_text(self) -> str:
        """Serializes current config state to custom text format."""
        lines = [
            f"BASE {self.base}",
            f"SPACING {' '.join(map(str, self.spacing))}",
        ]
        if self.side:
            lines.append(f"SIDE {self.side}")
        if self.position:
            lines.append(f"POSITION {self.position}")
        if self.species:
            lines.append(f"SPECIES {self.species}")

        # Nuclei / DAPI
        lines.append(f"DAPI {self.nuclei.path}")
        lines.append(f"DAPI_v0 {self.nuclei.v0}")
        lines.append(f"DAPI_v1 {self.nuclei.v1}")

        # Dynamic Genes
        for gene_name, ch in self.channels.items():
            lines.append(f"{gene_name} {ch.path}")
            lines.append(f"{gene_name}_v0 {ch.v0}")
            lines.append(f"{gene_name}_v1 {ch.v1}")

        if self.surface:
            lines.append(f"SURFACE {self.surface}")

        return "\n".join(lines) + "\n"

    @classmethod
    def from_config_text(cls, text: str) -> "PipelineConfig":
        raw_data = {}
        for line in text.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                raw_data[parts[0]] = parts[1]

        base = Path(raw_data.pop("BASE"))
        spacing_vals = tuple(map(float, raw_data.pop("SPACING").split()))
        side = raw_data.pop("SIDE", None)
        position = raw_data.pop("POSITION", None)
        surface = Path(raw_data.pop("SURFACE")) if "SURFACE" in raw_data else None
        species = raw_data.pop("SPECIES", None)

        channel_paths, channel_v0, channel_v1 = {}, {}, {}
        for key, value in raw_data.items():
            if key.endswith("_v0"):
                channel_v0[key[:-3]] = float(value)
            elif key.endswith("_v1"):
                channel_v1[key[:-3]] = float(value)
            else:
                channel_paths[key] = value

        nuclei_channel = None
        channels = {}

        for ch_name, ch_path in channel_paths.items():
            ch_obj = ChannelConfig(
                path=Path(ch_path),
                v0=channel_v0[ch_name],
                v1=channel_v1[ch_name],
            )
            if ch_name.upper() in {"DAPI", "NUCLEI"}:
                nuclei_channel = ch_obj
            else:
                channels[ch_name] = ch_obj

        if not nuclei_channel:
            raise ValueError("Missing mandatory nuclei (DAPI) channel configuration.")

        return cls(
            base=base,
            spacing=spacing_vals, # type: ignore
            nuclei=nuclei_channel,
            channels=channels,
            side=side,
            position=position,
            surface=surface,
            species=species,
        )