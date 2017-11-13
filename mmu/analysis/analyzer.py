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

            raw_pdf_data = self.__pdf_analyzer.get_raw_data(issue_file)


