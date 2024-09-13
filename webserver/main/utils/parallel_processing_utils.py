# we will be using thread based dummy tool for io based processing
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool as ProcessPool

from main.config import get_config_by_name


def io_bound_parallel_computation(function, iterator):
    pool = ThreadPool(processes=get_config_by_name('PARALLEL_PROCESSES'))
    results = pool.map(function, iterator)
    pool.close()
    pool.join()
    return results


def compute_bound_parallel_computation(function, iterator):
    pool = ProcessPool(get_config_by_name('PARALLEL_PROCESSES'))
    results = pool.map(function,iterator)
    pool.close()
    pool.join()
    return results
