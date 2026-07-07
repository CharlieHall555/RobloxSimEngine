import unittest
from classes.lua_classes.nil import nil

class NilTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(nil == nil , True)
        self.assertEqual(nil == False , False)
        self.assertEqual(nil == True , False)

if __name__ == '__main__':
    unittest.main()
    input()