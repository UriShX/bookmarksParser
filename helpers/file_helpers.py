import os
import re
from pathlib import Path


def check_dir_exists(dir_name:str) -> None:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
