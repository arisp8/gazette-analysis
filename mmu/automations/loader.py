import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import os
import errno
import glob
import os.path
import datetime

from mmu.db.handlers.issue import IssueHandler
from mmu.utility.helper import Helper

# @todo: Catch a few common exceptions that may appear at some points
# selenium.common.exceptions.NoSuchWindowException - When chrome's driver is closed

class Loader:

    __source = ""
    # Holds the id's of the issues that may appear on the search page
    __possible_issues = range(1,16)
    __driver = None

    def __init__(self, source):
        self.__source = source
        self.download_links = []
        self.download_folder = os.path.join(os.getcwd(), 'pdfs')

        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": os.getcwd() + "\pdfs"}
        chromeOptions.add_experimental_option("prefs", prefs)

        # @todo: Replace hard paths with relative paths and make sure that all needed stuff is downloaded in setup
        self.__driver = webdriver.Chrome(r"C:\Users\user\Documents\Aris\chromedriver.exe", chrome_options=chromeOptions)

        self.__issue_handler = IssueHandler()

    def file_exists(self, directory, file_name, file_extension = 'pdf'):
        return os.path.isfile(os.getcwd() + "\\" + directory + "\\" + file_name + '.' + file_extension)

    def find_start_number(self, type, year):
        conditions = {"type": [type], "date": [Helper.date_to_unix_timestamp(year), '>']}
        issues = self.__issue_handler.load_all(conditions=conditions)

        return len(issues)

    def download_all_issues(self, type, year):

        driver = self.__driver
        driver.get(self.__source)

        # Indicates whether or not more searches will be needed to find all results
        additional_issues = True

        # Find the issue type
        issue_type = driver.find_element_by_id("label-issue-id-" + str(type)).text

        # Indicates at which issue the next search must start
        num_start = self.find_start_number(issue_type, str(year))

        # Selects the year of the issues
        year_select = Select(driver.find_element_by_name("year"))
        year_select.select_by_value(str(year))

        # Checks the box for this certain type of issues
        driver.find_element_by_name("chbIssue_" + str(type)).click()


        while additional_issues:

            # Filters the search by issue number
            driver.find_element_by_name("fekNumberFrom").clear()
            driver.find_element_by_name("fekNumberFrom").send_keys(str(num_start))
            driver.find_element_by_name("fekNumberTo").clear()
            driver.find_element_by_name("fekNumberTo").send_keys(str(num_start + 200))

            # Submits the search form
            driver.find_element_by_name("search").click()

            # Waits 1 second for the results to load
            time.sleep(1)

            count = 0
            num_results = 0

            # Gets the amount of results from the messages displayed.
            for element in driver.find_elements_by_xpath('//div[@class="non-printable"]'):
                count += 1
                if "Βρέθηκαν" in element.text:
                    # @todo: Try regex instead of search loop and do some benchmarking
                    words = element.text.split(" ")
                    for index, word in enumerate(words):
                        if word == "αποτελέσματα":
                            num_results = int(words[index-1])
                    break

            # If there are no results for the search we abort
            if num_results == 0:
                print("No results have been found")
                break

            # The maximum number of results is 200, so if the result contains 200 an additional search will be needed
            if num_results < 200:
                additional_issues = False
            else:
                num_start += 200

            # By default we'll see the first page of results, well.. first
            active_page = 1

            # Gets the pagination list items
            pages = driver.find_elements_by_class_name("pagination_field")
            num_pages = len(pages)

            for current_page in range(0, num_pages):

                # Extract and handle download links.
                self.extract_download_links(driver.page_source, issue_type)

                # We have to re-find the pagination list because the DOM has been rebuilt.
                pages = driver.find_elements_by_class_name("pagination_field")
                # Loads the next page of results
                if current_page + 1 < len(pages):
                    pages[current_page + 1].click()
                    time.sleep(1)

    def handle_download(self, download_page, params):

        # First we get the redirect link from the download page
        html = Helper.get_url_contents(download_page)
        beautiful_soup = BeautifulSoup(html, "html.parser")
        meta = beautiful_soup.find("meta", {"http-equiv": "REFRESH"})
        download_link = meta['content'].replace("0;url=", "")

        # We do the same process twice because it involves 2 redirects.
        beautiful_soup = BeautifulSoup(Helper.get_url_contents(download_link), "html.parser")
        meta = beautiful_soup.find("meta", {"http-equiv": "REFRESH"})
        download_link = meta['content'].replace("0;url=", "")

        if Helper.download(download_link, params['issue_title'] + ".pdf", self.download_folder):
            issue_file = os.path.join(self.download_folder, params['issue_title'] + ".pdf")
            self.__issue_handler.create(params['issue_title'], params['issue_type'], params['issue_number'],
                                        issue_file, params['issue_date'])

    def extract_download_links(self, html, issue_type):

        beautiful_soup = BeautifulSoup(html, "html.parser")
        result_table = beautiful_soup.find("table", {"id": "result_table"})
        rows = result_table.find_all("tr")

        # We ignore the first 2 rows and the last one
        for row in rows[2:-1]:
            cells = row.find_all("td")
            info_cell = cells[1].find("b")
            download_cell = cells[2].find_all("a")

            info_cell_text = info_cell.get_text()
            info_cell_text = ' '.join(info_cell_text.split())
            info_cell_parts = info_cell_text.split(" - ")

            issue_title = info_cell_text
            issue_date = info_cell_parts[1]
            issue_number = re.sub(pattern=r'ΦΕΚ ([Α-Ω]?.?)+ ', repl="", string=issue_title)

            # Skip saved items
            if self.__issue_handler.load_by_title(issue_title):
                continue

            date_parts = issue_date.split(".")
            issue_unix_date = datetime.datetime(day=int(date_parts[0]), month=int(date_parts[1]),
                                                year=int(date_parts[2]))

            download_path = download_cell[1]['href'] if len(download_cell) > 1 else download_cell[0]['href']
            download_link = "http://www.et.gr" + download_path
            params = {"issue_title": issue_title, "issue_date": issue_unix_date, "issue_number": issue_number,
                      "issue_type": issue_type}
            self.handle_download(download_link, params)

    def scrape_pdfs(self):

        # Creates the pdfs folder if not exists
        try:
            os.makedirs('pdfs')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        year = 2017
        for i in self.__possible_issues:
            self.download_all_issues(i, year)
