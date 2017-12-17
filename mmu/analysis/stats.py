from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

from copy import deepcopy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import plotly.plotly as py
import plotly.graph_objs as go

plt.rcParams['figure.figsize'] = (16, 9)
plt.style.use('ggplot')

class Stats:

    # @param signatures A list of signatures.
    @staticmethod
    def measure_co_responsibilities(signatures):
        regulations = {}

        for signature in signatures:
            if signature['regulation'] not in regulations:
                regulations[signature['regulation']] = []

            if signature['role'] != 'Ο ΠΡΟΕΔΡΟΣ ΤΗΣ ΔΗΜΟΚΡΑΤΙΑΣ':
                regulations[signature['regulation']].append(signature)

        ministries = {}
        for regulation in regulations:
            current_regulation_ministries = []

            for signature in regulations[regulation]:

                if signature['ministry'] not in current_regulation_ministries:
                    current_regulation_ministries.append(signature['ministry'])

            for index, ministry in enumerate(current_regulation_ministries):
                if not ministry in ministries:
                    ministries[ministry] = {}

                for item in current_regulation_ministries[0:index] + current_regulation_ministries[index:]:

                    if item != ministry and item not in ministries[ministry]:
                        ministries[ministry][item] = 0

                    if item != ministry:
                        ministries[ministry][item] += 1

        total_per = 0
        items = 0
        for ministry in ministries:
            connections = ministries[ministry]

            labels = []
            values = []

            total_connections = 0

            for connection in connections:
                total_connections += connections[connection]

            others = 0
            for connection in connections:
                if connections[connection] / total_connections >= 0.03:
                    labels.append(connection)
                    values.append(connections[connection])
                else:
                    others += connections[connection]

            explode = ()
            for value in values:
                if value / total_connections > 0.2:
                    explode += (0.1,)
                else:
                    explode += (0,)

            if others > 0:
                labels.append('Υπόλοιποι')
                values.append(others)
                explode += (0,)

            if total_connections > 40:
                plt.title(ministry)
                pie,text,test = plt.pie(values, explode=explode, shadow=True, startangle=90, autopct='%1.0f%%')
                plt.legend(pie, labels, loc="best")
                plt.axis('equal')
                plt.tight_layout()
                plt.show()

    # Currently in development.
    @staticmethod
    def cluster_signature_data(signatures):
        # Euclidean Distance Caculator
        def dist(a, b, ax=1):
            return np.linalg.norm(a - b, axis=ax)

        ministries = {}
        ministries_count = 1
        regulations = {}
        regulations_count = 1

        for signature in signatures:
            regulation = signature['regulation']
            ministry = signature['ministry']

            if ministry not in ministries:
                ministries[ministry] = ministries_count
                ministries_count += 1

            if regulation not in regulations:
                regulations[regulation] = regulations_count
                regulations_count += 1

            signature['ministry_id'] = ministries[ministry]
            signature['regulation_id'] = regulations[regulation]

        regs = []
        mins = []
        for signature in signatures:
            regs.append(signature['regulation_id'])
            mins.append(signature['ministry_id'])

        X = np.array(list(zip(regs, mins)))
        plt.scatter(regs, mins, c='black', s=7)

        plt.show()

        # # Number of clusters
        # k = 3
        # # X coordinates of random centroids
        # C_x = np.random.randint(0, np.max(X) - 20, size=k)
        # # Y coordinates of random centroids
        # C_y = np.random.randint(0, np.max(X) - 20, size=k)
        # C = np.array(list(zip(C_x, C_y)), dtype=np.float32)
        # print(C)
        #
        # plt.scatter(regs, mins, c='#050505', s=7)
        # plt.scatter(C_x, C_y, marker='*', s=200, c='g')
        #
        # # To store the value of centroids when it updates
        # C_old = np.zeros(C.shape)
        # # Cluster Lables(0, 1, 2)
        # clusters = np.zeros(len(X))
        # # Error func. - Distance between new centroids and old centroids
        # error = dist(C, C_old, None)
        # # Loop will run till the error becomes zero
        # while error != 0:
        #     # Assigning each value to its closest cluster
        #     for i in range(len(X)):
        #         distances = dist(X[i], C)
        #         cluster = np.argmin(distances)
        #         clusters[i] = cluster
        #     # Storing the old centroid values
        #     C_old = deepcopy(C)
        #     # Finding the new centroids by taking the average value
        #     for i in range(k):
        #         points = [X[j] for j in range(len(X)) if clusters[j] == i]
        #         C[i] = np.mean(points, axis=0)
        #     error = dist(C, C_old, None)
        #
        # colors = ['r', 'g', 'b', 'y', 'c', 'm']
        # fig, ax = plt.subplots()
        # for i in range(k):
        #     points = np.array([X[j] for j in range(len(X)) if clusters[j] == i])
        #     ax.scatter(points[:, 0], points[:, 1], s=7, c=colors[i])
        # ax.scatter(C[:, 0], C[:, 1], marker='*', s=200, c='#050505')
        #
        # plt.show()