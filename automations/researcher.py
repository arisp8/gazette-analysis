import datetime
import urllib.request, urllib.parse, json, collections

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

            # Performs an http request and returns the response

    def wiki_search(self, keyword, limit = 10, lang = 'el'):
        link = "https://{lang}.wikipedia.org/w/api.php?"
        f = {'action' : 'opensearch', 'search' : keyword, 'limit' : limit, 'namespace' : 0,
             'format' : 'json', 'profile' : 'fuzzy'}
        link = link.format(lang=lang) + urllib.parse.urlencode(f)
        return self.get_url_contents(link, 'json')

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

    def research(self):
        # The year the researcher will start looking for. Note that
        current_year = self.__year_from
        cabinet_results = self.wiki_search(keyword='Κυβέρνηση', limit=50)


        while current_year <= self.__year_to:
            for key, cabinet in enumerate(cabinet_results[1]):
                if str(current_year) in cabinet:
                    title = cabinet
                    description = cabinet_results[2][key]
                    link = cabinet_results[3][key]
                    print(link)

            current_year += 1
