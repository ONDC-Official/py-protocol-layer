# we will be using thread based dummy tool for io based processing
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool as ProcessPool


def io_bound_parallel_computation(function, iterator):
    pool = ThreadPool(processes=100)
    results = pool.map(function, iterator)
    pool.close()
    pool.join()
    return results


def compute_bound_parallel_computation(function, iterator):
    pool = ProcessPool(10)
    results = pool.map(function,iterator)
    pool.close()
    pool.join()
    return results
