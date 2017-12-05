import unittest
from mmu.utility.helper import Helper
import datetime

class HelperTest(unittest.TestCase):

    def test_normalize_greek_name(self):
        self.assertEqual(Helper.normalize_greek_name("Παναγιώτης Καμμένος"), "ΠΑΝΑΓΙΩΤΗΣ ΚΑΜΜΕΝΟΣ")
        self.assertEqual(Helper.normalize_greek_name("Αγλαΐα Τεστ"), "ΑΓΛΑΙΑ ΤΕΣΤ")

    def test_date_to_unix_timestamp(self):
        self.assertEqual(Helper.date_to_unix_timestamp("22 Ιανουαρίου 2016"), datetime.datetime(2016, 1, 22))
        self.assertEqual(Helper.date_to_unix_timestamp("08 Αυγούστου 1922"), datetime.datetime(1922, 8, 8))
        self.assertEqual(Helper.date_to_unix_timestamp("1952"), datetime.datetime(1952, 1, 1))

        # That's my birthday
        self.assertEqual(Helper.date_to_unix_timestamp("21-08-1998"), datetime.datetime(1998, 8, 21))
        self.assertEqual(Helper.date_to_unix_timestamp("21/08/1998"), datetime.datetime(1998, 8, 21))

        # Testing date conversion with random strings interfering
        self.assertEqual(Helper.date_to_unix_timestamp("21 Ιανουαρίου 1972τεστ"), datetime.datetime(1972, 1, 21))
        self.assertEqual(Helper.date_to_unix_timestamp("1983rr"), datetime.datetime(1983, 1, 1))

    def test_clear_annotations(self):
        self.assertEqual(Helper.clear_annotations("Κινδυνεύει με αφανισμό (IUCN 3.1) [1]"), "Κινδυνεύει με αφανισμό (IUCN 3.1) ")


if __name__ == '__main__':
    unittest.main()