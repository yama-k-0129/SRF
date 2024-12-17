from dataclasses import dataclass
from typing import Union

@dataclass
class GISMetadata:
    nx: int
    ny: int
    xllcorner: float
    yllcorner: float
    cellsize: float
    nodata: Union[int, float]