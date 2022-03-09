import time
from threading import Thread
import multiprocessing as mp
import math
import concurrent
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import codecs
import datetime


def fibonacci(n):
    if n <= 0:
        return []
    if n == 1:
        return [0]
    if n == 2:
        return [0, 1]
    result = [0, 1]
    for i in range(n - 2):
        result.append(result[-1] + result[-2])
    return result


def integrate(f, a, b, *, n_jobs=1, n_iter=1000):
    acc = 0
    step = (b - a) / n_iter
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc


def run_easy():
    n = 10
    num = 100000

    with open('artifacts/easy.txt', 'w') as f:
        threads = [Thread(target=fibonacci, args=(num,)) for _ in range(n)]
        start = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        end = time.time()
        f.write(f'threading: {end - start}\n')

        processes = [mp.Process(target=fibonacci, args=(num,)) for _ in range(n)]
        start = time.time()
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        end = time.time()
        f.write(f'multiprocessing: {end - start}')


def run_medium():
    with open('artifacts/medium.txt', 'w') as f:
        f.write(f'  n_jobs  |     multiprocessing     |        threading        \n')
        f.write(f'______________________________________________________________\n')
        a = 0
        b = math.pi / 2
        cpu_num = mp.cpu_count()
        for workers in range(1, 2 * cpu_num + 1):
            threads = []
            res = 0
            start = time.time()
            with ThreadPoolExecutor(max_workers=workers) as executor:
                for i in range(workers):
                    s = (b - a) / workers * i
                    e = (b - a) / workers * (i + 1)
                    threads.append(executor.submit(integrate, math.cos, s, e))
                for thread in concurrent.futures.as_completed(threads):
                    res += thread.result()
            end = time.time()
            threading_time = end - start

            processes = []
            res = 0
            start = time.time()
            with ProcessPoolExecutor(max_workers=workers) as executor:
                for i in range(workers):
                    s = (b - a) / workers * i
                    e = (b - a) / workers * (i + 1)
                    processes.append(executor.submit(integrate, math.cos, s, e))
                for process in concurrent.futures.as_completed(processes):
                    res += process.result()
            end = time.time()
            mp_time = end - start

            f.write(f'    {workers}     |  {mp_time}  |  {threading_time}  \n')


def worker_a(in_queue, out_queue):
    while True:
        if not in_queue.empty():
            message = in_queue.get().lower()
            out_queue.put(message)
            time.sleep(5)


def worker_b(in_queue, out_queue):
    while True:
        if not in_queue.empty():
            message = codecs.encode(in_queue.get(), 'rot_13')
            out_queue.put(message)


def run_hard():
    main_to_a = mp.Queue()
    a_to_b = mp.Queue()
    b_to_main = mp.Queue()

    A = mp.Process(target=worker_a, args=(main_to_a, a_to_b), daemon=True)
    B = mp.Process(target=worker_b, args=(a_to_b, b_to_main), daemon=True)

    logs = []

    A.start()
    B.start()

    while True:
        message = input('>>> ')
        logs.append(f'Message: "{message}" | Time: {datetime.datetime.now()}')
        if message == 'exit':
            logs.append(f'Exit: {datetime.datetime.now()}')
            break
        main_to_a.put(message)
        message = b_to_main.get()
        logs.append(f'Encoded: "{message}" | Time: {datetime.datetime.now()}\n')

    with open('artifacts/hard.txt', 'w') as f:
        f.write('\n'.join(logs))


if __name__ == '__main__':
    run_easy()
    run_medium()
    run_hard()
