from mmu.db.handlers.issue import IssueHandler
from mmu.analysis.pdf_parser import CustomPDFParser
import re

class Analyzer:

    def __init__(self):
        self.__issue_handler = IssueHandler()
        self.__pdf_analyzer = CustomPDFParser()

        # Compile regular expressions that will be used a lot
        self.__date_pattern = re.compile(r"[α-ωΑ-Ωά-ώϊ-ϋΐ-ΰ]+,\s+?[0-9]{1,2}\s+?[α-ζΑ-Ζά-ώϊ-ϋΐ-ΰ]+\s+?[0-9]{4,4}")
        self.__illegal_chars = re.compile(r"\d+")

    # Checks whether or not a string indicates that parsing should stop.
    def is_break_point(self, word):
        if len(word) == 0:
            return False
        elif self.__illegal_chars.search(word):
            return True
        else:
            return False

    # Finds all occurences of a substring in a string
    # @return The indexes of all matched substrings.
    def find_all(self, key, string):
        matches = []
        start = 0
        searching = True
        while searching:
            index = string.find(key, start)

            if index == -1:
                searching = False
            else:
                matches.append(index)
                start = index + 1

        return matches

    # Analyzes the text from the pdf files to extract all signatures
    def extract_signatures_from_text(self, text):
        start_keys = ["Οι Υπουργοί\n", "Οι Αναπληρωτές Υπουργοί\n"]
        end_key = "Θεωρήθηκε και τέθηκε η Μεγάλη Σφραγίδα του Κράτους."
        starting_indexes = []

        for key in start_keys:
            starting_indexes += self.find_all(key, text)

        if len(starting_indexes) > 1:
            print(starting_indexes)

        if not starting_indexes:
            starting_indexes = [m.start() for m in self.__date_pattern.finditer(text)]

        # Ending indexes are useful when available, but availability is not guaranteed
        ending_indexes = self.find_all(end_key, text)

        for key, index in enumerate(starting_indexes):
            persons = []

            # Indicates whether or not the substring contains non-required information after the signatures
            # Is True when a valid ending index has been found
            end = (key < len(ending_indexes) and ending_indexes[key] > index)

            if end:
                to = ending_indexes[key]
                substring = text[index:to]
            else:
                substring = text[index:]

            words = substring.split("\n")

            # Iterates through words after the starting key
            role = ""
            for word in words[1:]:

                # If a valid ending point has not been found, then the first non-word will surely indicate the end of
                # the signatures.
                if not end and self.is_break_point(word):
                    break

                if len(word) > 3 and word.upper() == word:
                    persons.append({"role" : role, "name" : word})
                    # Reset role for the next one
                    role = ""
                else:
                    role += word

            print(persons)



    def start_analysis(self):
        # word1 = "ΝΙΚΟΛΑΟΣ ΚΟΤΖΙΑΣ "
        # word2 = " "
        # word3 = ""
        # word4 = "52"
        # word5 = "\x0c32"
        # word6 = "Καποδιστρίου 54"
        # print(self.is_break_point(word1))
        # print(self.is_break_point(word2))
        # print(self.is_break_point(word3))
        # print(self.is_break_point(word4))
        # print(self.is_break_point(word5))
        # print(self.is_break_point(word6))
        # exit()

        # Loads all issues not yet analyzed
        issues = self.__issue_handler.load_all({'analyzed' : [0]})

        for issue in issues:
            issue_id = issue['id']
            issue_file = issue['file']
            issue_number = issue['number']

            pdf_text = self.__pdf_analyzer.get_pdf_text(issue_file)
            pdf_images = self.__pdf_analyzer.get_pdf_images(issue_file, issue_id)

            if pdf_text:
                print("Extracting signatures from issue {}".format(issue_number))
                text_signatures = self.extract_signatures_from_text(pdf_text)



