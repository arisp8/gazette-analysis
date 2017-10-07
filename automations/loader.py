import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Loader:

    __source = ""
    # Holds the id's of the issues that may appear on the search page
    __possible_issues = range(0,16)
    __driver = None

    def __init__(self, source):
        self.__source = source
        print(self.__possible_issues)
        self.__driver = webdriver.Chrome(r"C:\Users\user\Documents\Aris\chromedriver.exe")

    def scrapePdfs(self):
        driver = self.__driver
        driver.get(self.__source)

        assert "ΦΕΚ" in driver.title

        for i in self.__possible_issues:

            num_start = 0

            try:
                print("chbIssue_" + str(i))
                driver.find_element_by_name("chbIssue_" + str(i)).click()

                try:
                    driver.find_element_by_name("search").click()
                except Exception as e:
                    print("Submit button not found")



            except Exception as e:
                print("Not found")
                # time.sleep(1)