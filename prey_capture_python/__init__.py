from prey_capture_python.analysis.extract_points import extract_points
from prey_capture_python.analysis.geometries import geometries
from prey_capture_python.analysis.prey_cap_metrics import preycap_metrics

from typing import Dict
import pandas as pd
from pathlib import Path
import sys
import typing
from typing import Optional, Union, Tuple, List, Dict
if sys.version_info.minor >= 8:
    from typing import Literal
else:
    from typing_extensions import Literal


def load_tracks(file:Path) -> Dict[str, pd.DataFrame]:
    return {'string': pd.DataFrame({'data':[1,2,3]})}

def use_tracks(path:str):
    tracks = load_tracks(path)
    tracks.a
