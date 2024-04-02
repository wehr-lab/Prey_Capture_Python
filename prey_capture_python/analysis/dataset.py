from dataclasses import dataclass
import numpy as np
import pandas as pd
import typing

@dataclass
class Track:
    pos: typing.List[int]
    p: typing.List[float]


@dataclass
class Track2D:
    xy: typing.List[Track, Track]
    

@dataclass
class Animal:
    parts: typing.List[str]
    
    @classmethod
    def from_df(df:pd.DataFrame) -> 'Animal':
        pass
    
class Cricket(Animal):
    front: Track2D
    back: Track2D
    parts = ['front', 'back']
    
class Mouse(Animal):
    pass
    
    
@dataclass
class Dataset:
    mouse: Mouse
    cricket: Cricket
    
    @property
    def azimuth(self):
        # whatever call azimuth with whatever it takes
        # return azimuth(self.mouse.front_paw.speed)
    
    @property
    def approaches(self):
        # return approaches(self.azimuth, self.mouse.speed)
        
        
class MyClass:
    def __init__(self, x, y):
        self._x = x
        self.y = y
        
        self._sum = None
        
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, x):
        self._sum = None
        self._x = x
        
    @property
    def sum(self):
        if self._sum is None:
            self._sum = self.x + self.y
        return self._sum
    
    