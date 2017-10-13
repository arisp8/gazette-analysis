import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import os
import os.path

# StaleElementReferenceException - Targetting element after DOM has been rebuilt
# WebDriverException - When chromedriver is closed

class Loader:

    __source = ""
    # Holds the id's of the issues that may appear on the search page
    __possible_issues = range(0,16)
    __driver = None

    def __init__(self, source):
        self.__source = source

        # @todo: Replace hard paths with relative paths and make sure that all needed stuff is downloaded in setup

        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": r"C:\Users\user\PycharmProjects\Mixed Up Ministries\mmu\pdfs"}
        chromeOptions.add_experimental_option("prefs", prefs)

        self.__driver = webdriver.Chrome(r"C:\Users\user\Documents\Aris\chromedriver.exe", chrome_options=chromeOptions)

    def file_exists(self, directory, file_name, file_extension = 'pdf'):
        return os.path.isfile(os.getcwd() + "\\" + directory + "\\" + file_name + '.' + file_extension)

    def downloadAllIssues(self, type, year, source):

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
                print(str(count) + ':' + element.text)
                count += 1
                if "Βρέθηκαν" in element.text:
                    # @todo: Try regex instead of search loop and do some benchmarking
                    words = element.text.split(" ")
                    for index, word in enumerate(words):
                        print(word)
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
                        fek_title = name_cell_text[0]
                        fek_date = name_cell_text[1]

                        # Presses the download button if the file is not already saved
                        if not self.file_exists('pdfs', fek_title):
                            download_cell.find_elements_by_tag_name("a")[1].click()
                            time.sleep(7)

                            # @TODO: Below solution not working for closing the tabs, need to find another one
                            # Closes the new download tab that has been opened
                            driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + '2')
                            driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL + 'w')

                            # Renames document.pdf to a relevant title
                            self.renameLatestDownload(fek_title)


                # We have to re-find the pagination list because the DOM has been rebuilt.
                pages = driver.find_elements_by_class_name("pagination_field")
                # Loads the next page of results
                if current_page + 1 < len(pages):
                    pages[current_page + 1].click()
                    time.sleep(1)

                    # Wait
                    # time.sleep(2)

    # Renames the downloaded pdfs from document.pdf to a more relevant title
    def renameLatestDownload(self, title, original_name = 'document.pdf'):
        directory = os.getcwd()
        original = directory + '\\pdfs\\' + original_name
        destination = directory + '\\pdfs\\' + title + '.pdf'

        if os.path.isfile(destination):
            print("Destination file already exists")
            return

        # We'll try 5 times in case the file hasn't been downloaded yet
        tries = 5
        while tries > 0:
            try:
                os.rename(original, destination)
                break
            except WindowsError as e    :
                print("Problem occured with the saving of: " + title)

            tries -= 1
            time.sleep(0.5)

        # @todo: Log download

    def scrapePdfs(self):

        year = 2017
        for i in self.__possible_issues:
            self.downloadAllIssues(i, year, self.__source)
