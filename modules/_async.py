# 异步运行函数，将函数放入线程池异步执行
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any

# 创建全局线程池
_async_thread_pool = ThreadPoolExecutor()

def _async(func: Callable, *args: Any, **kwargs: Any) -> Future:
    """异步执行函数（将函数放入线程池异步执行）
    Args:
        func: 要异步执行的函数
        *args, **kwargs: 函数的参数
    
    Returns:
        Future对象，可以通过future.result()获取结果，如果不需要结果可以忽略返回值

    Example:
        ```python
        future = _async(a, 1, 2, b=3)
        # 可以在其他地方继续执行其他任务
        print("其他任务")

        result = future.result()  # 阻塞等待结果
        ```
    """
    return _async_thread_pool.submit(func, *args, **kwargs)