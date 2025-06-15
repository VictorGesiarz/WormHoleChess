from multiprocessing import Process, Manager
import multiprocessing
import time
import math
import random

# Fake CPU-heavy computation
def heavy_computation(x):
    result = 0
    for i in range(1, 10_000):
        result += math.sin(x * i) ** 2 + math.cos(x * i) ** 2
    return result

# Worker function
def simulate(shared_dict, inputs, worker_id):
    for x in inputs:
        score = heavy_computation(x)
        shared_dict[x] = score
        # print(f"[Worker {worker_id}] Computed score for {x}: {score:.2f}")

def run_parallel(inputs, num_workers=16):
    with Manager() as manager:
        shared_dict = manager.dict()
        chunks = [inputs[i::num_workers] for i in range(num_workers)]
        processes = []

        start = time.time()

        for i in range(num_workers):
            p = Process(target=simulate, args=(shared_dict, chunks[i], i))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        end = time.time()
        print(f"\nParallel time: {end - start:.2f} seconds")
        return dict(shared_dict)

def run_sequential(inputs):
    results = {}
    start = time.time()
    for x in inputs:
        results[x] = heavy_computation(x)
    end = time.time()
    print(f"\nSequential time: {end - start:.2f} seconds")
    return results

if __name__ == '__main__':
    # 100 items to compute
    input_values = [random.uniform(0, 100) for _ in range(1000)]

    print("Running sequentially...")
    seq_results = run_sequential(input_values)
    # print(seq_results)

    cpu_count = multiprocessing.cpu_count()
    print('\nCPUs:', cpu_count)
    print("\nRunning in parallel...")
    par_results = run_parallel(input_values, num_workers=cpu_count)
    # print(par_results)