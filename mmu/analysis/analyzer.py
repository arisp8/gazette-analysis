from mmu.db.handlers.issue import IssueHandler

class Analyzer:

    def __init__(self):
        self.__issue_handler = IssueHandler()

    def start_analysis(self):
        issues = self.__issue_handler.load_all()
        print(issues)