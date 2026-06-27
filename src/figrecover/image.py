from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image

_HEX_RE = re.compile(r"^#([0-9a-fA-F]{6})$")


def load_rgb_array(path: Path) -> tuple[np.ndarray, int, int]:
    image = Image.open(path).convert("RGB")
    array = np.asarray(image)
    height, width = array.shape[:2]
    return array, width, height


def parse_hex_color(color: str) -> np.ndarray:
    match = _HEX_RE.match(color.strip())
    if not match:
        raise ValueError(f"Expected #RRGGBB colour, got {color!r}")
    hex_value = match.group(1)
    return np.array(
        [int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16)],
        dtype=np.float32,
    )


def color_mask(rgb: np.ndarray, color: str, *, tolerance: float) -> np.ndarray:
    target = parse_hex_color(color)
    delta = rgb.astype(np.float32) - target.reshape(1, 1, 3)
    return np.linalg.norm(delta, axis=2) <= tolerance
