import urllib
from urllib.request import Request
import shutil
import urllib.parse
import os
import json
import collections
import datetime
import re

# Helper class that defines useful formatting and file handling functions
class Helper:

    # Turns a greek name to all caps and without accents
    # @todo: Use regex or other way to speed up
    @staticmethod
    def normalize_greek_name(name):
        # α, β, γ, δ, ε, ζ, η, θ, ι, κ, λ, μ, ν, ξ, ο, π, ρ, σ, τ, υ, φ, χ, ψ, ω
        name = name.upper()
        replace_accents = {'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ϊ': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ϋ': 'Υ', 'Ώ': 'Ω'}

        for accent in replace_accents:
            if accent in name:
                name =  name.replace(accent, replace_accents[accent])

        return name

    @staticmethod
    # Performs an http request and returns the response
    def get_url_contents(link, content_type=''):
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

    @staticmethod
    def download(url, file_name= None, folder = os.getcwd()):
        @staticmethod
        def get_file_name(open_request):
            if 'Content-Disposition' in open_request.info():
                # If the response has Content-Disposition, try to get filename from it
                cd = dict(map(
                    lambda x: x.strip().split('=') if '=' in x else (x.strip(), ''),
                    open_request.info()['Content-Disposition'].split(';')))
                if 'filename' in cd:
                    filename = cd['filename'].strip("\"'")
                    if filename:
                        return filename

            # If no filename was found above, parse it out of the final URL.
            return os.path.basename(urllib.parse.urlsplit(open_request.url)[2])

        request = Request(url)
        r = urllib.request.urlopen(request)

        try:
            if not file_name:
                file_name = get_file_name(r)

            file_path = os.path.join(folder, file_name)

            with open(file_path, 'wb') as f:
                shutil.copyfileobj(r, f)
        finally:
            r.close()
            return True

    # Converts a textual date to a unix timestamp
    def date_to_unix_timestamp(self, date, lang='el'):
        if lang == 'el':
            d = 0
            m = 1
            y = 2
            months = {'Ιανουαρίου': 1, 'Φεβρουαρίου': 2, 'Μαρτίου': 3, 'Απριλίου': 4, 'Μαΐου': 5, 'Ιουνίου': 6,
                      'Ιουλίου': 7, 'Αυγούστου': 8, 'Σεπτεμβρίου': 9, 'Οκτωβρίου': 10, 'Νοεμβρίου': 11,
                      'Δεκεμβρίου': 12, 'Μαίου': 5}
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
        else:
            return 0
        date = self.clear_annotations(date)
        parts = date.split(separator)

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
            return 0

        return datetime.datetime(year=int(year), month=int(month), day=int(day))