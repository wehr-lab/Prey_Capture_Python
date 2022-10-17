from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Optional, ClassVar, List

import pandas as pd
import tables
import numpy as np

from prey_capture_python.data.model import Model
from prey_capture_python.data.position import Prey_Geometry, Position
from prey_capture_python.data.utils import datetime_str

# suppress the most obnoxious warning
import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

@dataclass
class Trial_Metadata(Model):
    """
    Metadata that describes a single trial!

    Attributes:
        condition (int): You can annotate your data fields here...
        laser_value
        circle
        filename
        folder_path
    """
    timestamp: datetime
    subject: str
    condition: int
    """
    You can document properties either in docstrings just below
    the attribute like this, or in the class-level docstring in the 
    "Attributes" field like above! and then readthedocs will render them for you!
    """
    laser_value: bool
    circle: bool
    filename: Path
    folder_path: Path

@dataclass
class Trial_Summary(Model):
    """
    Summary data computed for each trial!
    """
    captureT: float
    freqapproach: float
    timetoapproach: float
    timetointercept: float
    prob_inter: float
    prob_capture: float

@dataclass
class Trial(Model):
    """
    Data model for a single prey capture trial.

    Note how I am combining multiple smaller models so you don't have to have one
    massive thing and can potentially use your other models for different things!


    .. todo::

        Molly fill in the data description!

    """
    metadata: Trial_Metadata
    summary: Trial_Summary
    geometry: Prey_Geometry
    mouse_position: Optional[Position] = None
    cricket_position: Optional[Position] = None

    STRUCTURE: ClassVar[dict] = {
        'metadata': 'node',
        'summary': 'node',
        'geometry': 'table',
        'mouse_position': 'table',
        'cricket_position': 'table'
    }
    """
    Using this for now, you could do this smarter by 
    adding attributes or subclasses to the relevant models,
    but i'll leave that up to you.
    
    This tells our class how to handle each of the relevant submodels,
    whether they contain 
    """

    def _make_nodes(self, h5f:tables.File, group:tables.Group, structure:dict) -> dict:
        nodes = {}
        group_path = group._v_pathname
        for k, v in structure.items():
            try:
                nodes[k] = h5f.get_node(group_path, k)
            except tables.NoSuchNodeError:
                if v == 'node':
                    nodes[k] = h5f.create_group(group_path, k, createparents=True)
                elif v == 'table':
                    # actually fuck this just use pandas to make the tables
                    nodes[k] = group_path + '/' + k
                    # description = getattr(self, k).make_description()
                    # nodes[k] = h5f.create_table(group_path, k, description=description)
                else:
                    raise ValueError(f"Node type must be either node or table, got {v}")

        return nodes



    def to_hdf(self,
               h5f:Optional[tables.File]=None,
               path:Optional[Path]=None):
        """
        Given either an open h5f file or a path to an output file,
        write to disk!

        Save within the hdf file like

        /subject/trial_date/...
        - metadata: a blank node to contain the metadata attributes
        - summary: a blank node to contain summary attributes
        - geometry: a table containing the geometry values
        - mouse_position/cricket_position: an optional table ...


        Args:
            h5f (:class:`tables.File`): An Open HDF5 file in write or append mode
            path (:class:`pathlib.Path`): A Path to an hdf5 file

        """
        if h5f is not None and path is not None:
            raise ValueError("Need to pass either h5f or path, but not both")

        if path:
            path = Path(path)
            # use some compression!
            filter = tables.Filters(complevel=9)
            h5f = tables.open_file(str(path), mode='a', filters=filter)

        # get path for our group
        group_path = f"/{self.metadata.subject}"
        group_name = f"{datetime_str(self.metadata.timestamp)}"
        # get or create group
        try:
            group = h5f.get_node(group_path + '/' + group_name)
        except tables.NoSuchNodeError:
            group = h5f.create_group(group_path, group_name, createparents=True)

        # make or get groups!
        nodes = self._make_nodes(h5f, group, self.STRUCTURE)
        h5f.flush()

        # dump our data into the things!
        for key, node in nodes.items():
            # if we made a group, that means we're dumping scalar metadata into it!
            if isinstance(node, tables.Group):
                # iterate through the dictionary of values in the model, assigning!
                for k, v in getattr(self, key).dict(hdf5_safe=True).items():
                    node._v_attrs[k] = v
                h5f.flush()
            elif isinstance(node, str):
                # Otherwise we just stashed the location where the dataframe should go!
                field = getattr(self, key) # type: Optional[Model]
                if field is None:
                    continue

                field.to_df().to_hdf(h5f.filename, key=node, mode='a')

        h5f.flush()
        h5f.close()

    @classmethod
    def list_sessions(cls, path:Path) -> dict:
        """
        See available subjects and sessions for a given hdf5 file

        Args:
            path: Path to hdf5 file!

        Returns:
            dict: {'subject':['session_1', 'session_2'], ...}
        """
        h5f = tables.open_file(str(path), mode='r')
        sessions = {}
        subjects = list(h5f.root._v_children.keys())
        for subject in subjects:
            sessions[subject] = list(h5f.root._v_children[subject]._v_children.keys())
        return sessions

    @classmethod
    def from_hdf(cls, path:Path, subject:str, session:str):
        h5f = tables.open_file(str(path), mode='r')
        try:
            group = h5f.get_node(f"/{subject}/{session}")
        except tables.NoSuchNodeError:
            raise ValueError(f"No session {session} found for {subject}, try using .list_sessions() to see available sessions")

        # make components!
        metadata = Trial_Metadata(**_read_attrs(group.metadata))
        summary = Trial_Summary(**_read_attrs(group.summary))

        # frick it i'm getting sleepy you get the idea and can clean this up later yno
        if 'geometry' in group._v_children:
            df = pd.read_hdf(str(path), f"/{subject}/{session}/geometry")
            geometry = Prey_Geometry.from_df(df)
        if 'mouse_position' in group._v_children:
            df = pd.read_hdf(str(path), f"/{subject}/{session}/mouse_position")
            mouse_position = Position.from_df(df)
        else:
            mouse_position = None
        if 'cricket_position' in group._v_children:
            df = pd.read_hdf(str(path), f"/{subject}/{session}/cricket_position")
            cricket_position = Position.from_df(df)
        else:
            cricket_position = None

        return Trial(metadata, summary, geometry, mouse_position, cricket_position)

    @classmethod
    def from_hdf_row(cls, row:pd.Series) -> 'Trial':
        """
        Load one trial's worth of data from existing bigass hdf5 format
        """
        # parse subject and timestamp from folder_path
        timestamp, subject = str(row['folder_path']).split('_mouse-')
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d_%H-%M-%S')

        return Trial(
            metadata=Trial_Metadata(
                timestamp = timestamp,
                subject = subject,
                condition = bool(row['condition']),
                laser_value= bool(row['laser_value']),
                circle = bool(row['circle']),
                filename = row['filename'],
                folder_path = row['folder_path']
            ),
            summary = Trial_Summary(
                captureT = row['captureT'],
                freqapproach = row['freqapproach'],
                timetoapproach = row['timetoapproach'],
                timetointercept = row['timetointercept'],
                prob_inter = row['prob_inter'],
                prob_capture = row['prob_capture']
            ),
            geometry= Prey_Geometry(
                dist=row['dist'],
                cricket_spd=row['cricket_spd'],
                mouse_spd=row['mouse_spd'],
                az=row['az']
            )
        )




def _read_attrs(group:tables.Group) -> dict:
    attrs = {}
    for attr in group._v_attrs._v_attrnamesuser:
        attrs[attr] = group._v_attrs[attr]
    return attrs



@dataclass
class TrialCollection:
    """
    Collector class for holding multiple trials worth of data, mostly
    for reading and loading the hdf5 files!
    """
    trials: List[Trial]

    @classmethod
    def from_oldstyle_hdf(cls, path) -> 'TrialCollection':
        df = pd.read_hdf(path)
        trials = []
        for idx, row in df.iterrows():
            trials.append(Trial.from_hdf_row(row))
        return TrialCollection(trials=trials)

    @classmethod
    def from_hdf(cls, path) -> 'TrialCollection':
        """Leaving this one up to you!"""
        pass

    def to_hdf(self, path):
        for trial in self.trials:
            trial.to_hdf(path=path)






def example_usage(allmice_path: Path) -> Trial:
    """
    This is an example of creating one of these trial
    Args:
        allmice_path:

    Returns:

    """
    subject = 'mysubject'
    session = datetime.now()

    meta = Trial_Metadata(
        timestamp=session,
        subject=subject,
        condition=1,
        laser_value=True,
        circle=True,
        filename=Path('here.csv'),
        folder_path=Path('./also_here')
    )

    summary =  Trial_Summary(
        captureT=100,
        freqapproach=200,
        timetoapproach=300,
        timetointercept=1,
        prob_inter=2.5,
        prob_capture=5.5
    )

    geometry = Prey_Geometry(
        dist= np.array([1,2,3,4.5]),
        cricket_spd = np.array([5.5,6,7,8]),
        mouse_spd= np.array([9.5,10,11,12]),
        az = np.array([12,13.5,14,15])
    )
    trial = Trial(
        metadata=meta,
        summary=summary,
        geometry=geometry
    )

    trial.to_hdf(path='my_test_file.h5')

    # should be the same
    reloaded_trial = Trial.from_hdf('my_test_file.h5', subject, datetime_str(session))

    # to convert the stacked style u can use the TrialCollection class
    # try
    # TrialCollection.from_oldstyle_hdf('path')

    return reloaded_trial






