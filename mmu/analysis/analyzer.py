from mmu.db.handlers.issue import IssueHandler
from mmu.analysis.pdf_parser import CustomPDFParser

class Analyzer:

    def __init__(self):
        self.__issue_handler = IssueHandler()
        self.__pdf_analyzer = CustomPDFParser()

    def start_analysis(self):
        issues = self.__issue_handler.load_all()

        for issue in issues:
            issue_id = issue['id']
            issue_file = issue['file']

            pdf_text = self.__pdf_analyzer.get_pdf_text(issue_file)
            pdf_images = self.__pdf_analyzer.get_pdf_images(issue_file, issue_id)
            print(pdf_text)


