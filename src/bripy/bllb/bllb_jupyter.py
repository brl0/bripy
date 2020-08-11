#!/usr/bin/env python
"""bllb Jupyter common imports."""
# pylint: disable=unused-wildcard-import, unused-import

from bripy.bllb.bllb_logging import logger, DBG, setup_logging
from bripy.bllb.bllb import get_imports

from warnings import filterwarnings
filterwarnings("ignore")

# Standard notebook settings configuration and imports
import os
import sys
from datetime import datetime
from pathlib import Path

# imports to sanitize title for file name
# from urllib.parse import quote_plus
# from unicodedata import normalize
from slugify import slugify

# Other standard library imports
import io, math, re, string, time, unicodedata
from time import sleep
from operator import itemgetter as iget, attrgetter as aget
from pprint import pprint as pp
import psutil

# External library imports
import numpy as np
import pandas as pd
from tqdm import tqdm_pandas

# IPython imports and configuration
import IPython
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.display import display, HTML

InteractiveShell.ast_node_interactivity = "all"
#pd.options.display.html.table_schema = True

from tqdm import tqdm_notebook as tqdm

# Import plotting tools
import matplotlib as mpl
import matplotlib.pyplot as plt

import seaborn as sns

import holoviews as hv
from holoviews import opts as hv_opts

# import hvplot.pandas
hv.extension("bokeh", "matplotlib")

#import pdvega

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
    from ubrl.bllb.bllb_jupyter import *
    from ubrl.bllb.bllb_logging import setup_logging

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
