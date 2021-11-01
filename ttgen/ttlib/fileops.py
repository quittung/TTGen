import os, json
from typing import Any


data_dir = "data/"
"""Path where data is stored, relative to project root."""


def setwd() -> None:
    """Sets working directory to project root.
    """    
    wd = os.path.abspath(__file__)

    # root/ttgen/ttlib/fileops.py -> remove last three
    for i in range (0, 3):
        wd = os.path.dirname(wd)
    os.chdir(wd)


def exists(fname: str) -> bool:
    """Checks if file or path exists.
        Wrapper for os.path.exists(fname).

    Args:
        fname (str): Path. 

    Returns:
        bool: True if path exists.
    """    
    return os.path.exists(fname)


def dump_json(obj: Any, fname: str) -> None:
    """Dumps an object to a json file.

    Args:
        obj (Any): Object to encode.
        fname (str): Filename of json file.
    """    
    if not os.path.exists(os.path.dirname(fname)): os.makedirs(os.path.dirname(fname))
    with open(fname, 'w') as fobj:
        json.dump(obj, fobj, indent = 2)


def load_json(fname: str) -> Any:
    """Loads a json file and returns the encoded object.

    Args:
        fname (str): Path to json file.

    Returns:
        Any: Object encoded in json file.
    """    
    with open(fname, 'r') as fobj:
        return json.loads(fobj.read())


def load_json_dir(path: str) -> list:
    """Loads a directory of json files into a list.
        Flattens any top level list into the returned list.

    Args:
        path (str): Path to folder.

    Returns:
        list: List containing data from json files.
    """    
    """loads a directory full of json encoded lists and flattens them into a single list"""
    lst = []
    for fname in os.listdir(path):
            lst += load_json(os.path.join(path,fname))
    return lst

# Set constant working directory in project root. 
setwd()