""" maybe usefull for all datapackage conversion..."""
import oemof.tabular
from oemof.tabular.datapackage import building
from pathlib import Path

path_script = Path('.').resolve()
path_datapackage = path_script.parent

import os
import importlib
import oemof.tabular.config.config

os.environ["OEMOF_TABULAR_FOREIGN_KEY_DESCRIPTORS_FILE"] = str(path_script / "custom_foreign_key_descriptors.json")

# Nur nötig, wenn die Konfiguration nach dem Import geändert wurde
importlib.reload(oemof.tabular.config.config)

# todo maybe set custom foreign keys as a file too?
# example see test_examples of tabular test

building.infer_metadata(
    package_name="meta_package",
    foreign_keys={
        "bus":[
            "conversion",
            "dispatchable",
            "excess",
            #"grid",
            "load",
        ],

        #"multi_grid":["multi_grid"],

        #"area":["area"],

        "profile": [
            "load",
        ],

        "from_to_bus": [
            "conversion"
        ],
    },
    path=path_datapackage,
    metadata_filename= "datapackage.json",
)
