from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

class Stats:

    # @param grouped_signatures A list of signatures grouped by their issue.
    @staticmethod
    def measure_co_responsibilities(grouped_signatures):
        ministries = {}

        total_issues = len(grouped_signatures)

        for issue in grouped_signatures:
            current_issue_ministries = []

            for signature in grouped_signatures[issue]:
                if signature['ministry'] not in current_issue_ministries:
                    current_issue_ministries.append(signature['ministry'])

            for index, ministry in enumerate(current_issue_ministries):
                if not ministry in ministries:
                    ministries[ministry] = {}

                for item in current_issue_ministries[0:index] + current_issue_ministries[index:]:

                    if item != ministry and item not in ministries[ministry]:
                        ministries[ministry][item] = 0

                    if item != ministry:
                        ministries[ministry][item] += 1


        total_per = 0
        items = 0
        for ministry in ministries:
            connections = ministries[ministry]
            for connection in connections:
                num = connections[connection]
                per = round(num / total_issues * 100, 2)
                total_per += per
                items += 1
                print("{first} has {num} connections with {second} ({per}%)".format(first=ministry,
                                                                                    num=num,
                                                                                    second=connection,
                                                                                    per=per))