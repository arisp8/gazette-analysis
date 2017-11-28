import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import os
import errno
import glob
import os.path
import datetime

from mmu.db.handlers.issue import IssueHandler

# @todo: Catch a few common exceptions that may appear at some points
# StaleElementReferenceException - Targetting element after DOM has been rebuilt
# selenium.common.exceptions.NoSuchWindowException - When chrome's driver is closed

class Loader:

    __source = ""
    # Holds the id's of the issues that may appear on the search page
    __possible_issues = range(1,16)
    __driver = None

    def __init__(self, source):
        self.__source = source


        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": os.getcwd() + "\pdfs"}
        chromeOptions.add_experimental_option("prefs", prefs)

        # @todo: Replace hard paths with relative paths and make sure that all needed stuff is downloaded in setup
        self.__driver = webdriver.Chrome(r"C:\Users\user\Documents\Aris\chromedriver.exe", chrome_options=chromeOptions)

        self.__issue_handler = IssueHandler()

    def file_exists(self, directory, file_name, file_extension = 'pdf'):
        return os.path.isfile(os.getcwd() + "\\" + directory + "\\" + file_name + '.' + file_extension)

    def download_all_issues(self, type, year):

        driver = self.__driver
        driver.get(self.__source)

        # Indicates whether or not more searches will be needed to find all results
        additional_issues = True

        # Indicates at which issue the next search must start
        num_start = 0

        # Selects the year of the issues
        year_select = Select(driver.find_element_by_name("year"))
        year_select.select_by_value(str(year))

        # Checks the box for this certain type of issues
        driver.find_element_by_name("chbIssue_" + str(type)).click()

        issue_type = driver.find_element_by_id("label-issue-id-" + str(type)).text

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
                # @TODO: Create SQLite database to log messages, save file names and dates etc.

                result_table = driver.find_element_by_id("result_table")
                rows = result_table.find_elements_by_tag_name("tr")

                # Goes through all table rows to get names, dates and download links
                for row in rows:
                    cells = row.find_elements_by_tag_name("td")
                    if len(cells) > 2:
                        name_cell = cells[1].find_element_by_tag_name("b")
                        download_cell = cells[2]

                        name_cell_text = name_cell.text.split(" - ")
                        issue_title = name_cell_text[0]
                        issue_date = name_cell_text[1]

                        issue_number = re.sub(pattern=r'ΦΕΚ ([Α-Ω]?.?)+ ', repl="", string=issue_title)

                        saved_issue = self.__issue_handler.load_by_title(issue_title)

                        # Presses the download button if the file is not already saved
                        if not saved_issue:
                            download_cell.find_elements_by_tag_name("a")[1].click()
                            time.sleep(7)

                            # Renames document.pdf to a relevant title
                            issue_file = self.rename_latest_download(issue_title)

                            # Closes the new download tab that has been opened
                            if len(driver.window_handles) > 1:
                                base_tab = driver.window_handles[0]
                                new_tab = driver.window_handles[1]
                                driver.switch_to.window(new_tab)
                                driver.close()
                                driver.switch_to.window(base_tab)

                            # If renaming was successful we log the download to the db
                            if issue_file:
                                date_parts = issue_date.split(".")
                                issue_unix_date = datetime.datetime(day=int(date_parts[0]), month=int(date_parts[1]),
                                                                    year=int(date_parts[2]))

                                self.__issue_handler.create(title=issue_title, type=issue_type, number=issue_number,
                                                            file=issue_file, date=issue_unix_date)


                # We have to re-find the pagination list because the DOM has been rebuilt.
                pages = driver.find_elements_by_class_name("pagination_field")
                # Loads the next page of results
                if current_page + 1 < len(pages):
                    pages[current_page + 1].click()
                    time.sleep(1)


    # Renames the downloaded pdfs from document.pdf to a more relevant title
    def rename_latest_download(self, title, original_name = 'document.pdf'):
        directory = os.getcwd()

        destination = directory + '\\pdfs\\' + title + '.pdf'
        list_of_files = glob.glob(directory + '\\pdfs\\*.pdf')
        latest_file = max(list_of_files, key=os.path.getctime)

        if os.path.isfile(destination):
            print("Destination file already exists")
            return

        success = False

        # We'll try 5 times in case the file hasn't been downloaded yet
        tries = 5
        while tries > 0:
            try:
                os.rename(latest_file, destination)
                success = True
                break
            except WindowsError as e:
                print("Problem occured with the saving of: " + title)

            tries -= 1
            time.sleep(0.5)

        # Returns the relative file location on success
        if success:
            return '\\pdfs\\' + title + '.pdf'
        else:
            return False

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
