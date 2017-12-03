import unittest
from mmu.utility.helper import Helper

class HelperTest(unittest.TestCase):

    def test_normalize_greek_name(self):
        self.assertEqual(Helper.normalize_greek_name("Παναγιώτης Καμμένος"), "ΠΑΝΑΓΙΩΤΗΣ ΚΑΜΜΕΝΟΣ")
        self.assertEqual(Helper.normalize_greek_name("Αγλαΐα Τεστ"), "ΑΓΛΑΙΑ ΤΕΣΤ")


if __name__ == '__main__':
    unittest.main()