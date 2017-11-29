import unittest
from mmu.analysis.analyzer import Analyzer

class AnalyzerTest(unittest.TestCase):

    analyzer = Analyzer()

    def test_format_role(self):
        roles = \
            {"Αναπληρωτής ΥπουργόςΔικαιοσύνης": "Αναπληρωτής Υπουργός Δικαιοσύνης",
             "Διαφάνειαςκαι": "Διαφάνειας και",
             "Δικαιοσύνης, Διαφάνειας καιΑνθρωπίνων Δικαιωμάτων": "Δικαιοσύνης, Διαφάνειας και Ανθρωπίνων Δικαιωμάτων",
             "ΕξωτερικώνΟικονομικών": "Εξωτερικών Οικονομικών",
             "Ναυτιλίαςκαι Νησιωτικής Πολιτικής": "Ναυτιλίας και Νησιωτικής Πολιτικής"}

        for wrong in roles:
            correct = roles[wrong]
            self.assertEqual(self.analyzer.format_role(wrong), correct)

    def test_is_break_point(self):
        false_cases = ["ΝΙΚΟΛΑΟΣ ΚΟΤΖΙΑΣ", " ", ""]
        true_cases = ["52", "\x0c32", "Καποδιστρίου 54"]

        for word in true_cases:
            self.assertTrue(self.analyzer.is_break_point(word))

        for word in false_cases:
            self.assertFalse(self.analyzer.is_break_point(word))


if __name__ == '__main__':
    unittest.main()