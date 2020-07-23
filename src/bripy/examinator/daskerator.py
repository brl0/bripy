"""examinator script using dask"""
import logging
import sys
from functools import partial
from itertools import chain
from pathlib import Path
from pprint import pprint

import click
import pandas as pd
from dask.distributed import Client, LocalCluster, get_client
from fsspec import get_fs_token_paths

from bripy.bllb.fs import get_dir_fs, get_stat_fs, is_dir, is_file


@click.command()
@click.argument("path")
def main(path):
    client = get_client()
    dirs = [path]
    files = []
    while len(dirs):
        futures = client.map(get_dir_fs, dirs)
        results = client.gather(futures)
        pprint([*zip(dirs, results)])
        dirs = [*filter(is_dir, chain(*results))]
        files.extend([*chain(*results)])
    process = partial(get_stat_fs, opt_md5=True)
    futures = client.map(process, files)
    results = client.gather(futures)
    df = pd.DataFrame(results)
    print("\n\n\n")
    pprint(files)
    print(df)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel("DEBUG")
    cluster = LocalCluster()
    client = Client(cluster)
    sys.exit(main())  # pragma: no cover
