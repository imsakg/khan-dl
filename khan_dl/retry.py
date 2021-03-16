"""Small injectable bounded retry primitive; cancellation always propagates."""
import time


def retry_call(operation, retries=3, exceptions=(OSError,), delay=1.0,
               maximum=30.0, sleep=time.sleep, on_retry=None):
    if retries < 0 or delay < 0 or maximum < 0:
        raise ValueError('retry counts and delays cannot be negative')
    wait = min(delay, maximum)
    for attempt in range(retries + 1):
        try:
            return operation()
        except exceptions as error:
            if attempt == retries:
                raise
            if on_retry is not None:
                on_retry(attempt + 1, error, wait)
            sleep(wait)
            wait = min(wait * 2, maximum)
