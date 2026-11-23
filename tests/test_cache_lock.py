from unittest import mock

from redis.exceptions import LockNotOwnedError

from donor_reporting_portal.libs import cache as cache_lib


class ExpiredLock:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        raise LockNotOwnedError("Cannot release a lock that's no longer owned")


def test_get_or_compute_ignores_expired_lock_release():
    values = {}
    calls = []
    fake_cache = mock.Mock()
    fake_cache.get.side_effect = lambda key, default=None: values.get(key, default)
    fake_cache.set.side_effect = lambda key, value, timeout=None: values.__setitem__(key, value)
    fake_cache.lock.return_value = ExpiredLock()

    def producer():
        calls.append(1)
        return {"value": 1}

    key = "drp:test:expired-lock"
    with mock.patch.object(cache_lib, "cache", fake_cache):
        assert cache_lib.get_or_compute(key, producer) == {"value": 1}
        assert cache_lib.get_or_compute(key, producer) == {"value": 1}

    assert calls == [1]
    fake_cache.lock.assert_called_once_with(f"{key}:lock", timeout=60, blocking_timeout=5)


def test_cache_lock_falls_back_when_backend_has_no_lock():
    fake_cache = mock.Mock(spec=["get", "set"])

    with mock.patch.object(cache_lib, "cache", fake_cache):
        with cache_lib.cache_lock("drp:test:no-lock"):
            pass
