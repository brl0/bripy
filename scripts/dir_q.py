from multiprocessing import JoinableQueue as Queue, freeze_support
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from time import sleep, perf_counter
from hashlib import md5

MAX_WORKERS = 2
EXECUTOR = ProcessPoolExecutor
q = Queue()
hash_q = Queue()
basepath = r'C:\Users\b_r_l\OneDrive\Documents\code\python'
q.put(basepath)

def dir_worker(item):
    path = Path(item)
    dirs_only = filter(Path.is_dir, path.iterdir())
    dir_str = map(str, dirs_only)
    dir_list = [*dir_str]
    return dir_list


def hash_file(file_item):
    hasher = md5()
    print(file_item)
    try:
        with open(file_item, 'rb') as file:
            content = file.read()
            hasher.update(content)
        hash_value = hasher.hexdigest()
        print(hash_value)
        return hash_value
    except Exception as error:
        print(f'ERROR: {error}')
        return ''

def hash_worker(dir_item):
    path = Path(dir_item)
    files_only = filter(Path.is_file, path.iterdir())
    files_str = map(str, files_only)
    file_hashes = map(hash_file, files_str)
    return [*file_hashes]

if __name__ == '__main__':
    freeze_support()
    print(perf_counter())
    with EXECUTOR(max_workers=MAX_WORKERS) as executor:
        in_dirs = 0
        out_dirs = 1
        in_list = list()
        out_list = [basepath, ]
        hash_count = 0
        sleeps = 0
        while not q.empty() and q.qsize():
            item = q.get()
            print(f'{in_dirs}: {item}')
            in_list.append(item)
            in_dirs += 1
            future_dirs = executor.submit(dir_worker, item)
            dirs = future_dirs.result()
            q_dirs = [*map(q.put, dirs)]
            #print(dirs)
            out_dirs += len(dirs)
            out_list.extend(dirs)
            future_hashes = executor.submit(hash_worker, item)
            q_hashes = [*map(hash_q.put, dirs)]
            hashes = future_hashes.result()
            print(hashes)
            hash_count += len(hashes)
            while len(dirs) and q.empty():
                print('\n\n\nSLEEPING!!!!!!!!!!!!!!!!!!!!!!!!!\n\n\n')
                sleeps += 1
                sleep(0.05)
            q.task_done()
        q.join()
        print(f'q size: {q.qsize()}')
        print(f'in_dirs: {in_dirs}')
        print(f'out_dirs: {out_dirs}')
        all_items = [*Path(basepath).rglob('*')]
        dirs_only = [*filter(Path.is_dir, all_items)]
        print(f'all_items: {len(all_items)}')
        print(f'hash_count: {hash_count}')
        print(f'dirs_only: {len(dirs_only)}')
        print(f'in_list: {len(in_list)}')
        print(f'out_list: {len(out_list)}')
        diff = set(in_list).symmetric_difference(set(out_list))
        print(f'{len(diff)}: {diff}')
        print(f'sleeps: {sleeps}')
        print(perf_counter())
    print('FIN')
