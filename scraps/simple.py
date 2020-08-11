from pathlib import Path
from queue import Queue
from time import perf_counter

from bripy.examinator.examinator import get_stat

basepath = r'C:\Users\b_r_l\OneDrive\Documents\code'

q = Queue()
q.put(basepath)

i = 0
results = []
while not q.empty() or q.qsize():
    item = q.get()
    #print(i, perf_counter(), item)
    i += 1
    path = Path(item)
    all_items = [*path.iterdir()]
    dirs = filter(Path.is_dir, all_items)
    [*map(q.put, dirs)]
    results.extend([*map(get_stat, all_items)])
print(len(results))
print('FIN', i, perf_counter())
