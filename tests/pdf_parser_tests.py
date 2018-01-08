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

    def test_one_regulation_per_document_2(self):

        correct_names = ['ΠΡΟΚΟΠΙΟΣ Β ΠΑΥΛΟΠΟΥΛΟΣ', 'ΝΙΚΟΛΑΟΣ ΤΟΣΚΑΣ', 'ΓΕΩΡΓΙΟΣ ΣΤΑΘΑΚΗΣ', 'ΕΛΕΝΑ ΚΟΥΝΤΟΥΡΑ',
                         'ΝΙΚΟΛΑΟΣ ΚΟΤΖΙΑΣ', 'ΝΙΚΟΛΑΟΣ ΠΑΡΑΣΚΕΥΟΠΟΥΛΟΣ', 'ΓΕΩΡΓΙΟΣ ΚΑΤΡΟΥΓΚΑΛΟΣ',
                         'ΕΥΚΛΕΙΔΗΣ ΤΣΑΚΑΛΩΤΟΣ', 'ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ']



        file_path = os.path.join(os.path.join(os.getcwd(), 'test_pdfs/'), 'ΦΕΚ A 12 - 01.02.2016.pdf')
        regulation = self.parser.get_signatures_from_pdf(file_path, str(2016))[0]
        names = []

        for signature in regulation['signatures']:
            names.append(signature['name'])

        self.assertListEqual(correct_names, names)
        self.assertEqual(regulation['number'], '4363')
        self.assertEqual(regulation['type'], 'NOMOΣ ΥΠ’ ΑΡΙΘ.')


if __name__ == '__main__':
    unittest.main()