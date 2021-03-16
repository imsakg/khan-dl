import unittest
from khan_dl.retry import retry_call


class RetryTests(unittest.TestCase):
    def test_exponential_backoff_and_success(self):
        attempts, sleeps = [], []
        def operation():
            attempts.append(1)
            if len(attempts) < 3:
                raise OSError('temporary')
            return 42
        self.assertEqual(retry_call(operation, retries=3, sleep=sleeps.append), 42)
        self.assertEqual(sleeps, [1, 2])

    def test_exhaustion_preserves_exception(self):
        error = OSError('offline')
        def fail():
            raise error
        with self.assertRaises(OSError) as caught:
            retry_call(fail, retries=0)
        self.assertIs(caught.exception, error)

    def test_does_not_retry_programming_errors(self):
        with self.assertRaises(TypeError):
            retry_call(lambda: 1 + 'a', sleep=lambda _: self.fail('slept'))

    def test_caps_delays(self):
        sleeps = []
        with self.assertRaises(OSError):
            retry_call(lambda: (_ for _ in ()).throw(OSError()), retries=4,
                       delay=3, maximum=5, sleep=sleeps.append)
        self.assertEqual(sleeps, [3, 5, 5, 5])
