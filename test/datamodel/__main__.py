import unittest
import os

def main():
    # Get the directory where this __main__.py file is located
    test_dir = os.path.dirname(__file__)
    
    # Discover and load all test_*.py files in this directory
    suite = unittest.defaultTestLoader.discover(start_dir=test_dir, pattern="*_test.py")

    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    main()