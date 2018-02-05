import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mmu.analysis.pdf_parser import CustomPDFParser

class PdfParserTest(unittest.TestCase):

    parser = CustomPDFParser()

    def test_one_regulation_per_document(self):
        correct_signatures = [{"role": "Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ", "name": "ΠΡΟΚΟΠΗΣ Β ΠΑΥΛΟΠΟΥΛΟΣ"},
                      {"role": "Ο ΥΠΟΥΡΓΟΣ ΝΑΥΤΙΛΙΑΣ ΚΑΙ ΝΗΣΙΩΤΙΚΗΣ ΠΟΛΙΤΙΚΗΣ", "name": "ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ"}]
        file_path = self.get_file_path('ΦΕΚ A 1 - 12.01.2016.pdf')
        regulation = self.parser.get_signatures_from_pdf(file_path, str(2016))[0]

        self.assertEqual(correct_signatures, regulation['signatures'])
        self.assertEqual(regulation['number'], '1')
        self.assertEqual(regulation['type'], 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ’ ΑΡΙΘΜ.')

    def test_one_regulation_per_document_2(self):

        correct_names = ['ΠΡΟΚΟΠΙΟΣ Β ΠΑΥΛΟΠΟΥΛΟΣ', 'ΝΙΚΟΛΑΟΣ ΤΟΣΚΑΣ', 'ΓΕΩΡΓΙΟΣ ΣΤΑΘΑΚΗΣ', 'ΕΛΕΝΑ ΚΟΥΝΤΟΥΡΑ',
                         'ΝΙΚΟΛΑΟΣ ΚΟΤΖΙΑΣ', 'ΝΙΚΟΛΑΟΣ ΠΑΡΑΣΚΕΥΟΠΟΥΛΟΣ', 'ΓΕΩΡΓΙΟΣ ΚΑΤΡΟΥΓΚΑΛΟΣ',
                         'ΕΥΚΛΕΙΔΗΣ ΤΣΑΚΑΛΩΤΟΣ', 'ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ']



        file_path = self.get_file_path('ΦΕΚ A 12 - 01.02.2016.pdf')
        regulation = self.parser.get_signatures_from_pdf(file_path, str(2016))[0]
        names = self.get_names_from_regulation(regulation)

        self.assertListEqual(correct_names, names)
        self.assertEqual(regulation['number'], '4363')
        self.assertEqual(regulation['type'], 'NOMOΣ ΥΠ’ ΑΡΙΘ.')

    def test_one_regulation_per_document_3(self):
        correct_names = ['ΣΤΑΥΡΟΣ ΚΟΝΤΟΝΗΣ', 'ΓΕΩΡΓΙΟΣ ΣΤΑΘΑΚΗΣ']
        file_path = self.get_file_path('ΦΕΚ A 132 - 06.09.2017.pdf')
        regulation = self.parser.get_signatures_from_pdf(file_path, str(2016))[0]

        names = self.get_names_from_regulation(regulation)

        self.assertListEqual(correct_names, names)
        self.assertEqual(regulation['number'], '93')
        self.assertEqual(regulation['type'], 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ’ ΑΡΙΘΜ.')

    def test_eu_law_with_lots_of_signatures(self):
        correct_names = ['ΠΡΟΚΟΠΙΟΣ Β ΠΑΥΛΟΠΟΥΛΟΣ', 'ΠΑΝΑΓΙΩΤΗΣ ΚΟΥΡΟΥΜΠΛΗΣ', 'ΧΡΙΣΤΟΦΟΡΟΣ ΒΕΡΝΑΡΔΑΚΗΣ',
                         'ΝΙΚΟΛΑΟΣ ΤΟΣΚΑΣ', 'ΙΩΑΝΝΗΣ ΜΟΥΖΑΛΑΣ', 'ΓΕΩΡΓΙΟΣ ΣΤΑΘΑΚΗΣ', 'ΕΛΕΝΑ ΚΟΥΝΤΟΥΡΑ', 'ΘΕΟΔΩΡΑ ΤΖΑΚΡΗ',
                         'ΠΑΝΑΓΙΩΤΗΣ ΚΑΜΜΕΝΟΣ', 'ΔΗΜΗΤΡΙΟΣ ΒΙΤΣΑΣ', 'ΝΙΚΟΛΑΟΣ ΦΙΛΗΣ', 'ΑΘΑΝΑΣΙΑ ΑΝΑΓΝΩΣΤΟΠΟΥΛΟΥ',
                         'ΚΩΝΣΤΑΝΤΙΝΟΣ ΦΩΤΑΚΗΣ', 'ΘΕΟΔΟΣΙΟΣ ΠΕΛΕΓΡΙΝΗΣ', 'ΝΙΚΟΛΑΟΣ ΚΟΤΖΙΑΣ', 'ΝΙΚΟΛΑΟΣ ΞΥΔΑΚΗΣ',
                         'ΙΩΑΝΝΗΣ ΑΜΑΝΑΤΙΔΗΣ', 'ΔΗΜΗΤΡΙΟΣ ΜΑΡΔΑΣ', 'ΝΙΚΟΛΑΟΣ ΠΑΡΑΣΚΕΥΟΠΟΥΛΟΣ', 'ΔΗΜΗΤΡΙΟΣ ΠΑΠΑΓΓΕΛΟΠΟΥΛΟΣ',
                         'ΓΕΩΡΓΙΟΣ ΚΑΤΡΟΥΓΚΑΛΟΣ', 'ΘΕΑΝΩ ΦΩΤΙΟΥ', 'ΟΥΡΑΝΙΑ ΑΝΤΩΝΟΠΟΥΛΟΥ', 'ΑΝΔΡΕΑΣ ΞΑΝΘΟΣ',
                         'ΠΑΥΛΟΣ ΠΟΛΑΚΗΣ', 'ΑΡΙΣΤΕΙΔΗΣ ΜΠΑΛΤΑΣ', 'ΣΤΑΥΡΟΣ ΚΟΝΤΟΝΗΣ', 'ΕΥΚΛΕΙΔΗΣ ΤΣΑΚΑΛΩΤΟΣ',
                         'ΤΡΥΦΩΝΑΣ ΑΛΕΞΙΑΔΗΣ', 'ΓΕΩΡΓΙΟΣ ΧΟΥΛΙΑΡΑΚΗΣ', 'ΠΑΝΑΓΙΩΤΗΣ ΣΚΟΥΡΛΕΤΗΣ', 'ΙΩΑΝΝΗΣ ΤΣΙΡΩΝΗΣ',
                         'ΧΡΗΣΤΟΣ ΣΠΙΡΤΖΗΣ', 'ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ', 'ΕΥΑΓΓΕΛΟΣ ΑΠΟΣΤΟΛΟΥ', 'ΝΙΚΟΛΑΟΣ ΠΑΠΠΑΣ']
        file_path = self.get_file_path('ΦΕΚ A 93 - 27.05.2016.pdf')
        regulation = self.parser.get_signatures_from_pdf(file_path, str(2016))[0]

        names = self.get_names_from_regulation(regulation)

        # The names may not match in order due to pdf structure anomalies, but we need to make sure all names are
        # retrieved correctly. Sorted is used to make sure we are comparing them in the same order.
        self.assertEqual(sorted(correct_names), sorted(names))
        self.assertEqual(regulation['number'], '4388')
        self.assertEqual(regulation['type'], 'NOMOΣ ΥΠ’ ΑΡΙΘΜ.')

    def test_2_regulation_types(self):
      correct_names = ['ΠΡΟΚΟΠΙΟΣ Β ΠΑΥΛΟΠΟΥΛΟΣ', 'ΝΙΚΟΛΑΟΣ ΤΟΣΚΑΣ']
      file_path = self.get_file_path("ΦΕΚ A 14 - 05.02.2016.pdf")

      regulations = self.parser.get_signatures_from_pdf(file_path, str(2016))

      self.assertEqual(self.get_names_from_regulation(regulations[0]), correct_names) 

    # Make sure no regulations are returned when parsing a document that doesn't contain relevant data
    def test_no_regulations(self):
      file_path = self.get_file_path("ΦΕΚ A 34 - 02.03.2016.pdf")

      regulations = self.parser.get_signatures_from_pdf(file_path, str(2016))
      self.assertEqual(regulations, None)


    # Because church regulations are not relevant to our research, but appear in FEK issues
    # we need to make sure we get valid meta data about the regulation type but we shouldn't extract
    # any signatures 
    def test_church_regulations(self):
      file_path = self.get_file_path("ΦΕΚ A 35 - 02.03.2016.pdf")
      expected_regulations = [
        {'type': 'ΚΑΝΟΝΙΣΜΟΣ', 'number': '283'},
        {'type': 'ΚΑΝΟΝΙΣΜΟΣ', 'number': '282'}
      ]
      regulations = self.parser.get_signatures_from_pdf(file_path, str(2016))
      self.assertEqual(regulations, expected_regulations)

    # In a pdf containing 3 presidential decrees we want to make sure we extract the correct signatures for each one
    def test_3_regulations_of_the_same_type(self):
      file_path = self.get_file_path("ΦΕΚ A 39 - 08.03.2016.pdf")
      regulations = self.parser.get_signatures_from_pdf(file_path, str(2016))

      # Make sure we have extracted all 3 regulations
      self.assertEqual(len(regulations), 3)

      # Now make sure one-by-one we have extracted the correct data.
      first = regulations[0]
      second = regulations[1]
      third = regulations[2]

      # Validate the regulation type
      self.assertEqual(first['type'], 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ')
      self.assertEqual(second['type'], 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ')
      self.assertEqual(third['type'], 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ')

      # Validate the regulation number
      self.assertEqual(first['number'], '24')
      self.assertEqual(second['number'], '25')
      self.assertEqual(third['number'], '26')

      first_names = ['ΠΡΟΚΟΠΙΟΣ Β ΠΑΥΛΟΠΟΥΛΟΣ', 'ΝΙΚΟΛΑΟΣ ΤΟΣΚΑΣ', 'ΓΕΩΡΓΙΟΣ ΣΤΑΘΑΚΗΣ', 'ΠΑΝΑΓΙΩΤΗΣ ΚΑΜΜΕΝΟΣ',
        'ΝΙΚΟΛΑΟΣ ΚΟΤΖΙΑΣ', 'ΝΙΚΟΛΑΟΣ ΠΑΡΑΣΚΕΥΟΠΟΥΛΟΣ', 'ΕΥΚΛΕΙΔΗΣ ΤΣΑΚΑΛΩΤΟΣ', 'ΧΡΗΣΤΟΣ ΣΠΙΡΤΖΗΣ',
        'ΘΕΟΔΩΡΟΣ ΔΡΙΤΣΑΣ']
      second_names = first_names
      third_names = ['ΠΡΟΚΟΠΙΟΣ Β ΠΑΥΛΟΠΟΥΛΟΣ', 'ΝΙΚΟΛΑΟΣ ΠΑΡΑΣΚΕΥΟΠΟΥΛΟΣ']
      # print(self.get_names_from_regulation(first))
      self.assertEqual(self.get_names_from_regulation(first), first_names, msg="Names extracted from the 1st regulation are wrong")
      self.assertEqual(self.get_names_from_regulation(second), second_names, msg="Names extracted from the 2nd regulation are wrong")
      self.assertEqual(self.get_names_from_regulation(third), third_names, msg="Names extracted from the 3rd regulation are wrong")


    # Helper method to get all names from a single signature set
    def get_names_from_regulation(self, regulation):
        names = []

        for signature in regulation['signatures']:
            names.append(signature['name'])
        return names

    def get_file_path(self, file_name):
    	return os.path.join(os.path.join(os.path.dirname(__file__), 'test_pdfs'), file_name)

if __name__ == '__main__':
    unittest.main()
