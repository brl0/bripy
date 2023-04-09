#!/usr/bin/env python
"""bllb Jupyter common imports."""
# pylint: disable=unused-wildcard-import, unused-import

from warnings import filterwarnings

from bripy.bllb.bllb import get_imports
from bripy.bllb.logging import DBG, logger, setup_logging

filterwarnings("ignore")

# Other standard library imports
import io
import math

# Standard notebook settings configuration and imports
import os
import re
import string
import sys
import time
import unicodedata
from datetime import datetime
from operator import attrgetter as aget
from operator import itemgetter as iget
from pathlib import Path
from pprint import pprint as pp
from time import sleep

# IPython imports and configuration
import IPython

# External library imports
import numpy as np
import pandas as pd
import psutil
from IPython.core.display import HTML, display
from IPython.core.interactiveshell import InteractiveShell

# imports to sanitize title for file name
# from urllib.parse import quote_plus
# from unicodedata import normalize
from slugify import slugify
from tqdm import tqdm_pandas

InteractiveShell.ast_node_interactivity = "all"
# pd.options.display.html.table_schema = True

import holoviews as hv

# Import plotting tools
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from holoviews import opts as hv_opts
from tqdm import tqdm_notebook as tqdm

# import hvplot.pandas
hv.extension("bokeh", "matplotlib")

# import pdvega

imports = get_imports(globals())
"""
TITLE = 'Common imports template'
LOGS = True
LOG_LEVEL = "WARNING"
WARNINGS = False
IPY_LOGS = False
SEED = 42

if not WARNINGS:
    from warnings import filterwarnings
    filterwarnings("ignore")

bllb_path = r"C:/Users/b_r_l/source/repos/ubrl"  # Windows
#bllb_path = r"/mnt/data/OneDrive/Documents/code/python/bllb"  # Docker
#bllb_path = r"/home/brl0/source/repos/ubrl"  # WSL

# Select matplotlib backend
#%matplotlib inline
%matplotlib ipympl
#%matplotlib widget
#%matplotlib notebook
# Using notebook twice may avoid some errors
#%matplotlib notebook

import sys
from pathlib import Path

bllb_path = str(Path(bllb_path).resolve())
sys.path.insert(0, bllb_path)
try:
    from bllb_jupyter import *
    from bllb_logging import setup_logging
except ImportError:
    from bripy.bllb.bllb_jupyter import *
    from bripy.bllb.logging import setup_logging

logger = setup_logging(enable=LOGS, lvl=LOG_LEVEL, std_lib=True)
DBG = logger.debug

np.random.seed(seed=SEED)

slug = slugify(TITLE, separator='_')
info = f'<h1>{TITLE}</h1><p><h2>{slug}</h2><p>'
display(HTML(info))
print('\n', datetime.now())
print('\n', IPython.sys_info(), '\n')

%reload_ext watermark
%watermark -p {imports}

#mplstyle.use(['dark_background', 'ggplot', 'fast'])
#sns.set(style='white', context='poster', rc={'figure.figsize':(8,6)})

print('\n\n')
%matplotlib --list

#  char '%' not required for magics
%automagic ON
#  loads aliases for executables on $PATH
#%rehashx
#  call functions without parentheses ()
%autocall 1
#  turn on/off pretty print explicitly (on by default)
#%pprint

#  enable logging: include output, raw input commands, time stamps included
#  log to file name
if IPY_LOGS:
    logname = slug + datetime.now().strftime('_%Y%m%d%H%M%S') + '.py.log'
    %logstart -o -r -t {logname} 'rotate'
"""
