from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DESIGN_TOKEN_PATH = Path(__file__).with_name("design_tokens.json")

try:
    with DESIGN_TOKEN_PATH.open("r", encoding="utf-8") as fp:
        DESIGN_TOKENS: dict[str, Any] = json.load(fp)
except FileNotFoundError:
    DESIGN_TOKENS = {}


def get_design_token(path: str, default: Any = None) -> Any:
    """Retrieve a nested design theme by dot-separated path."""
    current: Any = DESIGN_TOKENS
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return default
        current = current[segment]
    return current


def theme(path: str, default: Any = None) -> Any:
    """Alias for get_design_token()."""
    return get_design_token(path, default)


## OG PRIMARY COLOR ##
##### "#0D7C66" ######