from dataclasses import dataclass, field


@dataclass
class CleanParams:
    v0: int
    v1: int
    gaussian_sigma: list[float] = field(default_factory=lambda: [6, 6, 6])
    frequency_cutoff: float = 0.05
    low_res_size: list[int] = field(default_factory=lambda: [512, 512, 296])
