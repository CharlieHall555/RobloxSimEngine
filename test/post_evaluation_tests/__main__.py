import os
import unittest


def main():
    test_dir = os.path.dirname(__file__)
    suite = unittest.defaultTestLoader.discover(start_dir=test_dir, pattern="*_test.py")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    main()
