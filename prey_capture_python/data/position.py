"""
Data models for positional data!
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union, List, Literal, Optional
import numpy.typing as npt
import numpy as np

from prey_capture_python.data.model import Model

@dataclass
class Position(Model):
    x: npt.NDArray[float]
    y: npt.NDArray[float]
    p: npt.NDArray[float]

@dataclass
class Prey_Geometry(Model):
    dist: npt.NDArray[float]
    cricket_spd: npt.NDArray[float]
    mouse_spd: npt.NDArray[float]
    az: npt.NDArray[float]




