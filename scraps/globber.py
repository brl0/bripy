from pathlib import Path
from time import perf_counter

basepath = r"C:\Users\b_r_l\OneDrive\Documents\code"

print(perf_counter())
path = Path(basepath)
all_items = [*path.rglob("*")]
dirs = filter(Path.is_dir, all_items)
print(len(all_items))
print("FIN", len([*dirs]), perf_counter())
