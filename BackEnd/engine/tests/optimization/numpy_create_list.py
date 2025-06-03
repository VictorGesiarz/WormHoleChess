from numba import njit
import numpy as np 
import time


@njit 
def reset_arrays(tests: int, size: int): 
    a = np.zeros(size, dtype=np.uint8)
    for _ in range(tests): 
        for i in range(23): 
            a[i] = 0

@njit
def create_arrays(tests: int, size: int):
    for _ in range(tests): 
        a = np.zeros(size, dtype=np.uint8) 


def test(): 
    tests = 100000 * 120 * 37 # Num of games to simulate, 120 moves per game max, 37 possible moves per turn on average
    print(f"Number of tests: {tests}")
    array_size = 2

    start = time.time()
    create_arrays(tests, array_size)
    end = time.time()
    print(f"Create array time: {end - start}")

    start = time.time()
    reset_arrays(tests, array_size)
    end = time.time()
    print(f"Reset array time: {end - start}")


test()