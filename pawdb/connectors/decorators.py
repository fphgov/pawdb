import time
import logging
from functools import wraps

# Configure the logger
logger = logging.getLogger("pawdb")


def log_execution_time(func):
    """Decorator to log the execution time and additional context of a method."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)  # Execute the wrapped function
        elapsed_time = time.time() - start_time

        # Log execution time and additional context
        log_data = {"method": func.__name__, "execution_time": f"{elapsed_time:.2f}s"}

        # If the function returns a dictionary with log context, merge it
        if isinstance(result, dict) and "log_context" in result:
            log_data.update(result["log_context"])
            result = result.get("data")  # Extract the actual data from the result

        logger.info(f"Method {func.__name__} executed.", extra=log_data)
        return result

    return wrapper
