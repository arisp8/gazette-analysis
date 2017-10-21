from mmu.db.handlers.ministry import MinistryHandler
import datetime
import urllib.request, urllib.parse, json, collections
from bs4 import BeautifulSoup

# Automatically finds information about past & current cabinet formations, ministers etc.
class Researcher:

    # Default constructor for the researcher
    def __init__(self, year_from = None, year_to = None):

        # If no limits are given, then we'll just research for this year
        if not year_from and not year_to:
            self.__year_from = datetime.datetime.today().year
            self.__year_to = datetime.datetime.today().year
        elif not year_from:
            # If only upper or lower limits are given but not both, then the researcher will just look for that year
            self.__year_to = year_to
            self.__year_from = year_to
        elif not year_to:
            # If only upper or lower limits are given but not both, then the researcher will just look for that year
            self.__year_from = year_from
            self.__year_to = year_from
        else:
            self.__year_from = year_from
            self.__year_to = year_to

        # Initialize ministry handler in default database (no arguments)
        self.__ministry_handler = MinistryHandler()

    # Uses wikipedia's API to perform searches and returns the results from the JSON response as a list
    def wiki_search(self, keyword, limit = 10, lang = 'el'):
        link = "https://{lang}.wikipedia.org/w/api.php?"
        f = {'action' : 'opensearch', 'search' : keyword, 'limit' : limit, 'namespace' : 0,
             'format' : 'json', 'profile' : 'fuzzy'}
        link = link.format(lang=lang) + urllib.parse.urlencode(f)
        return self.get_url_contents(link, 'json')

    # Performs an http request and returns the response
    def get_url_contents(self, link, content_type=''):
        try:
            with urllib.request.urlopen(link) as url:
                response = url.read().decode("utf-8")

                if content_type == 'json':
                    s = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(response)
                    return s
                else:
                    return response

        except urllib.error.HTTPError as e:
            print(e)
            return {}
        except urllib.error.URLError as e:
            print(e)
            return {}

    # Clears text from useless remaining markup elements
    def clear_text(self, text):
        text = text.replace("\n", "").replace("\xa0", " ").replace("\xa02", " ")
        return text

    # Parses the HTML markup and returns useful formatted information
    def markup_information(self, markup):

        type = ''
        if not markup:
            return None

        if markup.find("ul"):
            type = 'list'
        elif markup.find("a", {"class": "external"}):
            type = 'link'
        else:
            type = 'text'

        if type == 'text':
            return self.clear_text(markup.get_text())
        elif type == 'list':
            list_items = markup.find("ul").find_all("li")
            values = []
            for item in list_items:
                values.append(self.clear_text(item.get_text()))

            return values

        elif type == 'link':
            anchor = markup.find("a")
            text = anchor.get_text()
            url = anchor.get('href')

            return {"text": text, "url": url}

    # Returns formatted information fetched from the table on the top right of wikipedia articles
    def wiki_article_info(self, link):
        html = self.get_url_contents(link)
        soup = BeautifulSoup(html, 'html.parser')
        table_rows = soup.find("table", {"class": "infobox"}).find_all("tr")

        information = {}

        for row in table_rows:
            if row.th:
                # @todo: Create function for the formatting
                header = self.clear_text(row.th.get_text()).lower()
                raw_value = row.td

                value = self.markup_information(raw_value)

                information[header] = value

        return information

    # Researches and saves ministries in specific
    def research_ministries(self):
        ministries_wiki = self.wiki_search(keyword='Υπουργείο', limit=75)

        # Article titles that are irrelevant
        ignore_titles = ['Υπουργείο' ,'Υπουργείο Παιδείας και Πολιτισμού της Κύπρου', 'Υπουργείο Άμυνας των ΗΠΑ',
                        'Υπουργείο Εσωτερικών (Κύπρος)', 'Υπουργείο Εσωτερικής Ασφάλειας των ΗΠΑ']


        for key, ministry_name in enumerate(ministries_wiki[1]):
            if ministry_name not in ignore_titles:
                ministry_description = ministries_wiki[2][key]
                wiki_link = ministries_wiki[3][key]

                print(ministry_name)
                print(ministry_description)
                print(wiki_link)
                print("\n\n")

                ministry_info = self.wiki_article_info(wiki_link)
                print(ministry_info)

    # Starts the research process
    def research(self):
        self.research_ministries()
