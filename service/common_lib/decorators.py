import functools
import time


def ttl_lru_cache(ttl_seconds, maxsize=16, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.

    Note that ttl "windows" are used, so cache entries are valid within the window they are created, but the TTL is
    just the MAX that the entry is valid.  It could be invalidated earlier than that.

    Example:
    @ttl_lru_cache(ttl_seconds=10)
    def expensive(a: int):
        time.sleep(1 * a)

    ttl_seconds: Time to live (TTL) for cached results (in seconds).  If set to 0 or None, then caching is turned OFF.
    maxsize: Maximum cache size (see `functools.lru_cache`).  This should be set to the limit you want within a single
    time window, as entries from old windows aren't pushed out until maxsize is hit.  So even if you never see more than
    a few unique keys, you will quickly fill up the cache as the values from each time "window" will stick around until
    maxsize is reached.
    typed: Cache on distinct input types (see `functools.lru_cache`).
    """

    def _decorator(fn):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            if ttl_seconds:
                return _new(*args, **kwargs, __time_salt=int(time.time() / ttl_seconds))
            else:
                return fn(*args, **kwargs)

        return _wrapped

    return _decorator
