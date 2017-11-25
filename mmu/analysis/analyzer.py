from mmu.db.handlers.issue import IssueHandler
from mmu.analysis.pdf_parser import CustomPDFParser

class Analyzer:

    def __init__(self):
        self.__issue_handler = IssueHandler()
        self.__pdf_analyzer = CustomPDFParser()

    # Finds all occurences of a substring in a string
    # @return The indexes of all matched substrings.
    def find_all(self, string, key):
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
        # print(text)
        signatures = self.find_all(text, "Οι Υπουργοί")
        for index in signatures:
            substring = text[index:]
            print(substring)


    def start_analysis(self):
        # Loads all issues not yet analyzed
        issues = self.__issue_handler.load_all({'analyzed' : [0]})

        for issue in issues:
            issue_id = issue['id']
            issue_file = issue['file']

            pdf_text = self.__pdf_analyzer.get_pdf_text(issue_file)
            pdf_images = self.__pdf_analyzer.get_pdf_images(issue_file, issue_id)

            text_signatures = self.extract_signatures_from_text(pdf_text)



