"""
Base class for our data modeling
"""
import numpy as np
import pandas as pd
import tables
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from prey_capture_python.data.utils import datetime_str

import pdb
@dataclass
class Model:

    def to_df(self) -> pd.DataFrame:
        fields = {
            field:getattr(self, field) \
            for field in self.__dataclass_fields__.keys() \
            if isinstance(getattr(self, field), np.ndarray)}
        # pad to length
        maxlen = max([arr.shape[0] for arr in fields.values()])
        for k, v in fields.items():
            if v.shape[0] < maxlen:
                fields[k] = np.pad(v, (0,maxlen-v.shape[0]), mode='constant', constant_values=np.nan)

        try:
            return pd.DataFrame(fields)
        except ValueError:
            pdb.set_trace()

    @classmethod
    def from_df(cls, df:pd.DataFrame) -> 'Model':
        return cls(**{k:df[k].to_numpy() for k in df.columns})

    def dict(self, hdf5_safe:bool=False) -> dict:
        ret = {}
        for k in self.__dataclass_fields__.keys():
            field = getattr(self, k)
            if isinstance(field, Model):
                field = field.dict(hdf5_safe)
            elif hdf5_safe and isinstance(field, datetime):
                field = datetime_str(field)
            elif hdf5_safe and isinstance(field, Path):
                field = str(field)
            ret[k] = field

        return ret

    @classmethod
    def make_description(cls) -> tables.MetaIsDescription:
        """
        Make pytables description from numpy dtypes
        Super janky. in the future you should probably make
        a more robust way of determining the data type for
        use with a pytables description
        """

        dtypes = np.dtype([
            (k,np.dtype(v.type.__args__[1].__args__[0])) for k,v in cls.__dataclass_fields__.items() if hasattr(v.type, 'dtype')
        ])
        # make nested dtype object
        description = tables.description.descr_from_dtype(dtypes)
        return description