import os, json



dirData = "data/"


def setwd():
    """sets working directory to project root"""
    wd = __file__
    # each root/ttgen/ttlib/fileops.py -> remove last three
    for i in range (0, 3):
        wd = os.path.dirname(wd)
    os.chdir(wd)

# set constant working directory in project root. is this hacky or unwise?
setwd()


def load_json(fname: str):
    """loads a json file and returns the corresponding object"""
    with open(fname, 'r') as fobj:
        return json.loads(fobj.read())


def load_json_dir(path: str):
    """loads a directory full of json encoded lists and flattens them into a single list"""
    lst = []
    for fname in os.listdir(path):
            lst += load_json(os.path.join(path,fname))
    return lst
