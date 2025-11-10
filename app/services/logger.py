import time
import logging
from functools import wraps

# Setup logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

def log_req(func):
    """Decorator untuk ngukur waktu eksekusi fungsi"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = round(time.time() - start, 2)
            logging.info(f"[TIMER] {func.__name__} executed in {elapsed}s")
            return result
        except Exception as e:
            logging.error(f"[ERROR] {func.__name__}: {e}")
            raise e
    return wrapper
