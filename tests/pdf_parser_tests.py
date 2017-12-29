import unittest
import os
from mmu.analysis.pdf_parser import CustomPDFParser

class PdfParserTest(unittest.TestCase):

    parser = CustomPDFParser()

    def test_one_regulation_per_document(self):
        correct_signatures = [{"role": "Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ", "name": "ΠΡΟΚΟΠΗΣ Β ΠΑΥΛΟΠΟΥΛΟΣ"},
                      {"role": "Ο ΥΠΟΥΡΓΟΣ ΝΑΥΤΙΛΙΑΣ ΚΑΙ ΝΗΣΙΩΤΙΚΗΣ ΠΟΛΙΤΙΚΗΣ", "name": "ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ"}]
        file_path = os.path.join(os.path.join(os.getcwd(), 'test_pdfs/'), 'ΦΕΚ A 1 - 12.01.2016.pdf')
        regulation = self.parser.get_signatures_from_pdf(file_path, str(2016))[0]

        self.assertEqual(correct_signatures, regulation['signatures'])
        self.assertEqual(regulation['number'], '1')
        self.assertEqual(regulation['type'], 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ’ ΑΡΙΘΜ.')

        correct_signatures = [{"role": "Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ", "name": "ΠΡΟΚΟΠΙΟΣ Β ΠΑΥΛΟΠΟΥΛΟΣ"},
                              {"role": "ΑΝΑΠΛΗΡΩΤΗΣ ΥΠΟΥΡΓΟΣ ΕΣΩΤΕΡΙΚΩΝ ΚΑΙ ΔΙΟΙΚΗΤΙΚΗΣ ΑΝΑΣΥΓΚΡΟΤΗΣΗΣ",
                               "name": "ΝΙΚΟΛΑΟΣ ΤΟΣΚΑΣ"},
                              {"role": "ΟΙΚΟΝΟΜΙΑΣ ΑΝΑΠΤΥΞΗΣ ΚΑΙ ΤΟΥΡΙΣΜΟΥ", "name": "ΓΕΩΡΓΙΟΣ ΣΤΑΘΑΚΗΣ"},
                              {"role": "ΑΝΑΠΛΗΡΩΤΡΙΑ ΥΠΟΥΡΓΟΣ ΟΙΚΟΝΟΜΙΑΣ ΑΝΑΠΤΥΞΗΣ ΚΑΙ ΤΟΥΡΙΣΜΟΥ",
                               "name": "ΕΛΕΝΑ ΚΟΥΝΤΟΥΡΑ"},
                              {"role": "ΕΞΩΤΕΡΙΚΩΝ", "name": "ΝΙΚΟΛΑΟΣ ΚΟΤΖΙΑΣ"},
                              {"role": "ΔΙΚΑΙΟΣΥΝΗΣ ΔΙΑΦΑΝΕΙΑΣ ΚΑΙ ΑΝΘΡΩΠΙΝΩΝ ΔΙΚΑΙΩΜΑΤΩΝ",
                               "name": "ΝΙΚΟΛΑΟΣ ΠΑΡΑΣΚΕΥΟΠΟΥΛΟΣ"},
                              {"role": "ΕΡΓΑΣΙΑΣ ΚΟΙΝΩΝΙΚΗΣ ΑΣΦΑΛΙΣΗΣ ΚΑΙ ΚΟΙΝΩΝΙΚΗΣ ΑΛΛΗΛΕΓΓΥΗΣ",
                               "name": "ΓΕΩΡΓΙΟΣ ΚΑΤΡΟΥΓΚΑΛΟΣ"},
                              {"role": "ΟΙΚΟΝΟΜΙΚΩΝ", "name": "ΕΥΚΛΕΙΔΗΣ ΤΣΑΚΑΛΩΤΟΣ"},
                              {"role": "ΝΑΥΤΙΛΙΑΣ ΚΑΙ ΝΗΣΙΩΤΙΚΗΣ ΠΟΛΙΤΙΚΗΣ", "name": "ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ"}]

        file_path = os.path.join(os.path.join(os.getcwd(), 'test_pdfs/'), 'ΦΕΚ A 12 - 01.02.2016.pdf')
        regulation = self.parser.get_signatures_from_pdf(file_path, str(2016))[0]

        print(regulation)

        self.assertEqual(correct_signatures, regulation['signatures'])
        self.assertEqual(regulation['number'], '4363')
        self.assertEqual(regulation['type'], 'NOMOΣ ΥΠ’ ΑΡΙΘ.')


    # def extracts_signatures_from_document_with_multiple_regulations(self):
    #     signatures = [{"role": "Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ", "name": "Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ"},
    #                   {"role": "Ο ΥΠΟΥΡΓΟΣ ΝΑΥΤΙΛΙΑΣ ΚΑΙ ΝΗΣΙΩΤΙΚΗΣ ΠΟΛΙΤΙΚΗΣ", "name": "ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ"}]
    #     print(os.getcwd())
    #     file_path = os.path.join(os.path.join(__file__, 'test_cases/'), 'ΦΕΚ A 1 - 12.01.2016.pdf')
    #     self.assertEqual(self.parser.get_signatures_from_pdf(file_path))


if __name__ == '__main__':
    unittest.main()