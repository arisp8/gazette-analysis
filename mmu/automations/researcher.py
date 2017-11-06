from mmu.db.handlers.ministry import MinistryHandler
from mmu.db.handlers.cabinet import CabinetHandler
import datetime
import urllib.request, urllib.parse, json, collections
import re
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

        # Initialize ministry & cabinet handler in default database (no arguments)
        self.__ministry_handler = MinistryHandler()
        self.__cabinet_handler = CabinetHandler()

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
    def wiki_synopsis_info(self, link):
        html = self.get_url_contents(link)
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table", {"class": "infobox"})

        try:
            table_rows = table.find_all("tr")
        except AttributeError as e:
            print("The information table wasn't found. Additional info: " + str(e))
            return {}

        information = {}

        for row in table_rows:
            if row.th:
                # @todo: Create function for the formatting
                header = self.clear_text(row.th.get_text()).lower()
                raw_value = row.td

                value = self.markup_information(raw_value)

                # Make sure value is not None
                if value:
                    information[header] = value

        return information

    def wiki_article_info(self, link):
        html = self.get_url_contents(link)
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find("div", {"id": "mw-content-text"}).find_all('table')

        for table in tables:
            rows = table.find_all('tr')

            try:
                ths = rows[0].find_all('th')
                headers = []
                for th in ths:
                    headers.append(th.get_text())
            except AttributeError:
                print("The table doesn't fit the format we're looking for")

            if not headers:
                continue

            print(headers)

    # Converts a textual date to a unix timestamp
    def date_to_unix_timestamp(self, date, lang = 'el'):
        if lang == 'el':
            d = 0
            m = 1
            y = 2
            months = {'Ιανουαρίου' : 1, 'Φεβρουαρίου' : 2, 'Μαρτίου' : 3, 'Απριλίου' : 4, 'Μαΐου' : 5, 'Ιουνίου' : 6,
                      'Ιουλίου' : 7, 'Αυγούστου' : 8, 'Σεπτεμβρίου' : 9, 'Οκτωβρίου' : 10, 'Νοεμβρίου' : 11,
                      'Δεκεμβρίου' : 12}
            text_month = False
            separator = " "
            pattern = "Α-Ωα-ωά-ώ"

        if re.match('[0-9]{1,2} [' + pattern + ']{1,} [0-9]{4,4}', date):
            separator = " "
            text_month = True
        elif re.match('[0-9]{1,2}-[0-9]{1,2}-[0-9]{,4}', date):
            separator = "-"
        elif re.match('[0-9]{1,2}/[0-9]{1,2}/[0-9]{,4}', date):
            separator = "/"
        elif re.match('[0-9]{4,4}', date):
            return datetime.datetime(year=int(date), month=1, day=1)

        parts = date.split(separator)
        print(parts)

        if d < len(parts):
            day = parts[d]
        else:
            day = 1

        if m < len(parts) and text_month:
            month = months[parts[m]]
        elif m in parts:
            month = parts[m]
        else:
            month = 1

        if y < len(parts):
            year = parts[y]
        else:
            year = 1970

        formatted_date = str(day) + "/" + str(month) + "/" + str(year)
        return datetime.datetime(year=int(year), month=int(month), day=int(day))

    # Creates new records for the ministries that we don't have saved
    def save_ministry(self, name, description, params):
        established = 0
        disbanded = 0

        if 'σύσταση' in params:
            established = self.date_to_unix_timestamp(params['σύσταση'])

        if 'κατάργηση' in params:
            disbanded = self.date_to_unix_timestamp(params['κατάργηση'])

        ministry = self.__ministry_handler.load_by_name(name)
        print(ministry)
        if not ministry:
            self.__ministry_handler.create(name, description, established, disbanded)

    def save_cabinet(self, title, description, params):

        date_from = 0
        date_to = 0

        if 'ημερομηνία σχηματισμού' in params:
            date_from = self.date_to_unix_timestamp(params['ημερομηνία σχηματισμού'])

        if 'ημερομηνία διάλυσης' in params:
            date_to = self.date_to_unix_timestamp(params['ημερομηνία διάλυσης'])

        cabinet  = self.__cabinet_handler.load_by_title(title)

        if not cabinet:
            self.__cabinet_handler.create(title, description, date_from, date_to)



    # Researches and saves ministries in specific
    # @todo: Use extra information to fill the ministry origins table
    def research_ministries(self):
        ministries_wiki = self.wiki_search(keyword='Υπουργείο', limit=75)

        # Article titles that are irrelevant
        ignore_titles = ['Υπουργείο' ,'Υπουργείο Παιδείας και Πολιτισμού της Κύπρου', 'Υπουργείο Άμυνας των ΗΠΑ',
                        'Υπουργείο Εσωτερικών (Κύπρος)', 'Υπουργείο Εσωτερικής Ασφάλειας των ΗΠΑ']


        for key, ministry_name in enumerate(ministries_wiki[1]):
            if ministry_name not in ignore_titles:
                ministry_description = ministries_wiki[2][key]
                wiki_link = ministries_wiki[3][key]

                ministry_info = self.wiki_synopsis_info(wiki_link)

                self.save_ministry(ministry_name, ministry_description, ministry_info)

    # Researches and saves information about cabinets
    def research_cabinets(self):
        # We find the current cabinet from the official government's website
        # current_cabinet_link = "https://government.gov.gr/kivernisi/"



        # Research previous cabinet from wikipedia since I couldn't find information elsewhere
        cabinets_wiki = self.wiki_search(keyword='Κυβέρνηση', limit=75)

        # Article titles that are irrelevant
        ignore_titles = ['Κυβέρνηση', 'Κυβέρνηση της Ελλάδας', 'Κυβέρνηση εθνικής σωτηρίας Μίλαν Νέντιτς 1941',
                         'Κυβέρνηση της Καταλονίας', 'Κυβέρνηση Μανουέλ Βαλλς', 'Κυβέρνηση του Καΐρου',
                         'Κυβέρνηση Εθνικής Αμύνης', 'Κυβέρνηση Καποδίστρια', 'Κυβέρνηση της Τσεχικής Δημοκρατίας',
                         'Κυβέρνηση του Ηνωμένου Βασιλείου Ντέιβιντ Κάμερον 2010', 'Κυβέρνηση Μίλαν Ατσίμοβιτς 1941',
                         'Κυβέρνηση του Ηνωμένου Βασιλείου', 'Κυβέρνηση Νίκου Αναστασιάδη 2013']
        #
        for key, cabinet_name in enumerate(cabinets_wiki[1]):
            if cabinet_name not in ignore_titles:
                cabinet_description = cabinets_wiki[2][key]
                wiki_link = cabinets_wiki[3][key]

                # cabinet_details = self.wiki_article_info(wiki_link)
                cabinet_info = self.wiki_synopsis_info(wiki_link)

                print(cabinet_info)

                self.save_cabinet(cabinet_name, cabinet_description, cabinet_info)

    # Starts the research process
    def research(self):
        self.research_ministries()
        self.research_cabinets()