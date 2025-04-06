import numpy  as np
import requests
import os

def get_key(filename:str, line:int)->str:
    """
    Goes into my super-secret api text file and gets my keys yurrr.

    args: Filename (str), line in file (int)

    returns: key

    """
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines[line-1]
