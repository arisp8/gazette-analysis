import os
import re
import io
import time

from subprocess import call
from PIL import Image

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.layout import LTContainer
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextLine
from pdfminer.layout import LTFigure
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.layout import LTChar
from pdfminer.pdfpage import PDFPage
from mmu.utility.helper import Helper

from timeit import default_timer as timer

class CustomPDFParser:

    def __init__(self):
        self.__project_path = os.getcwd()

        # Initialize required objects
        self.laparams = LAParams()

    def get_pdf_text(self, file_name):
        try:
            text = self.convert_pdf_to_txt(file_name)
        except FileNotFoundError:
            print("The file with the name {} was not found.".format(file_name))
            text = ""
        return text

    # Uses libpoppler's pdfimages tool to extract all images from the pdf and then uses PIL to convert from ppm to jpg
    # @return A list of image paths extracted from this pdf
    def get_pdf_images(self, file_path, id):
        directory = self.__project_path + '/images/' + str(id)
        images = []
        if not os.path.exists(directory):
            os.makedirs(directory)
            call(['pdfimages', file_path, directory +  "/" + str(id)])

        files = os.listdir(directory)

        for file in files:
            image_path = os.path.join(directory, file)
            # Convert .ppm images to jpg
            if '.ppm' in image_path:
                image = Image.open(image_path)
                image_path = image_path.replace(".ppm", ".jpg")
                image.save(image_path)
            images.append(image_path)



        return images

    # Analyzes the structure of the pdf file to correctly extract the signatures from the document.
    def get_signatures_from_pdf(self, path):
        codec = 'utf-8'
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr=rsrcmgr,laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        pages = PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True)

        # Analyze first page to get a feel of what's going on
        try:
            first_page = next(pages)
            interpreter.process_page(first_page)
        except StopIteration:
            print("The pdf document may be damaged")
            return

        first_page_layout = device.get_result()
        useful_data = self.get_document_info(first_page_layout)

        # for page in pages:
        #     self.get_document_info(page)

    def text_from_layout_objects(self, objects, text=[]):
        self.in_character_sequence = False
        text_content = []
        # print(objects)
        try:
            for layout_object in objects:
                # print(layout_object)
                # if isinstance(layout_object, LTTextBoxHorizontal):
                #     for child in layout_object:
                #         print(child)
                #     print("\n")

                if isinstance(layout_object, LTContainer):
                    self.in_character_sequence = False
                    word = ""
                    for child in layout_object:
                        word += self.text_from_layout_objects(child, text_content)
                    if '***' in word:
                        word += "***"

                    text_content.append(word)
                elif isinstance(layout_object, LTChar):
                    if not self.in_character_sequence and "-Bold" in layout_object.fontname:
                        text_content.append("***")
                    text_content.append(layout_object.get_text())
                    self.in_character_sequence = True
                elif isinstance(layout_object, LTTextBox) or isinstance(layout_object, LTTextLine):
                    self.in_character_sequence = False
                    text_content.append(layout_object.get_text())

            if text:
                delimiter = ''
            else:
                delimiter = "\n"
            return delimiter.join(text_content)

        except TypeError:
            return ""

    def find_regulations(self, action, type, text_items, index=0):
        regulations = []
        regulation_nums = []
        plural_to_singular = {'ΚΑΝΟΝΙΣΜΟΙ': "ΚΑΝΟΝΙΣΜΟΣ",
                              'ΠΡΟΕΔΡΙΚΑ ΔΙΑΤΑΓΜΑΤΑ': "ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ",
                              'ΠΡΑΞΕΙΣ ΥΠΟΥΡΓΙΚΟΥ ΣΥΜΒΟΥΛΙΟΥ': 'ΠΡΑΞΗ ΥΠΟΥΡΓΙΚΟΥ ΣΥΜΒΟΥΛΙΟΥ'}

        def find_regulations_from_multiple_types(text_items):
            multiple = self.get_types('multiple')

            for item in text_items[index:]:

                if len(regulations) > 1 and re.match(r"\*\*\*\s+\*\*\*", item):
                    print("Stopping")
                    break

                if '***' in item:
                    item = item.replace("***", "").strip()
                    if item in multiple:
                        type = item

                if '...' in item:
                    all_matches = re.findall(r"(\d{1,}\.)([\s\w]+)()", item)
                    for match in all_matches:
                        num = match[0]
                        # Make sure it's not already added
                        if num not in regulation_nums:
                            regulations.append({'type': plural_to_singular[type], 'number': num})
                            regulation_nums.append(num)

        def find_multiple_regulations(text_items):

            for item in text_items[index:]:
                if type in plural_to_singular and plural_to_singular[type] in item:
                    search = re.search(r"\d?\d{1,4}?", item)
                    num = search.group(0)
                    if num not in regulation_nums:
                        regulations.append({'type': plural_to_singular[type], 'number': num})
                        regulation_nums.append(num)

        def find_single_regulation(text_items):

            for item in text_items[index:]:
                if type in item:
                    print(item)
                    search = re.search(r"\d?\d{1,4}?", item)
                    num = search.group(0)
                    regulations.append({'type': type.replace(num, "").strip(), 'number': num})
                    break

        if action == "multiple_regulation_types":
            find_regulations_from_multiple_types(text_items)
            return regulations
        elif action == "multiple_regulations":
            find_multiple_regulations(text_items)
            return regulations
        elif action == "single_regulation":
            find_single_regulation(text_items)
            return regulations

    def get_types(self, type = 'single'):
        if type == 'single':
            return ['ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ’ ΑΡΙΘΜ.', "ΝΟΜΟΣ ΥΠ’ ΑΡΙΘ.", "ΝΟΜΟΣ ΥΠ’ ΑΡΙθ.", "NOMOΣ ΥΠ’ ΑΡΙΘ.",
                   'ΚΑΝΟΝΙΣΜΟΣ ΥΠ’ ΑΡΙΘΜ.', 'ΝΟΜΟΣ ΥΠ’ ΑΡΙΘΜ.', 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ΄ ΑΡΙΘΜ.', 'NOMOΣ ΥΠ’ ΑΡΙΘΜ.',
                   'NOMOΣ ΥΠ’ ΑΡΙΘM.', 'NOMOΣ ΥΠ΄ΑΡΙΘΜ.', 'ΝΟΜΟΣ ΥΠ’ ΑΡΙΘM.', "ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ' ΑΡΙΘΜ."]
        elif type == 'multiple':
            return ['ΚΑΝΟΝΙΣΜΟΙ','ΑΠΟΦΑΣΕΙΣ', 'ΠΡΑΞΕΙΣ ΥΠΟΥΡΓΙΚΟΥ ΣΥΜΒΟΥΛΙΟΥ', 'ΠΡΟΕΔΡΙΚΑ ΔΙΑΤΑΓΜΑΤΑ',
                    'ΑΝΑΚΟΙΝΩΣΕΙΣ', 'AΠΟΦΑΣΕΙΣ', 'ΑΠΟΦΑΣΕΙΣ ΤΗΣ ΟΛΟΜΕΛΕΙΑΣ ΤΗΣ ΒΟΥΛΗΣ']
        elif type == 'ignore':
            return ['ΒΟΥΛΗ ΤΩΝ ΕΛΛΗΝΩΝ', 'ΔΙΟΡΘΩΣΕΙΣ ΣΦΑΛΜΑΤΩΝ', 'ΑΠΟΦΑΣΕΙΣ ΤΗΣ ΟΛΟΜΕΛΕΙΑΣ ΤΗΣ ΒΟΥΛΗΣ']

    # Analyzes the first page of a pdf document to extract useful info about the laws being analyzed.
    def get_document_info(self, page):

        text_items = self.text_from_layout_objects(page).split("\n")
        # print('Text items: ', text_items)

        # This list will contain information regarding all regulations inside the parsed document. Regulations may be:
        # -- Laws
        # -- Presidential Decrees
        # -- Ministerial Decisions
        regulations = []

        # These keywords indicate that the document contains more than one regulation and that they are described in the
        # table of contents.
        multiple = self.get_types('multiple')

        # These keywords indicate that the document contains a single regulation of the same type as the keyword
        single =  self.get_types('single')

        # These starting titles let us know that the document doesn't contain relevant data.
        ignore = self.get_types('ignore')

        # Indicates the course of action we need to take for our analysis
        action = ""
        # The type of law this document contains (Most of the times it's a signle type)
        type = ""
        # Shows where the way ahead was found
        index = -1

        for i, possible_title in enumerate(text_items[4:10]):
            if possible_title.strip() == 'ΠΕΡΙΕΧΟΜΕΝΑ':
                action = "multiple_regulation_types"
                index = i
                break
            for item in multiple:
                if item in possible_title:
                    action = "multiple_regulations"
                    type = possible_title
                    index = i
                    break
            for item in single:
                if item in possible_title:
                    action = "single_regulation"
                    type = possible_title
                    index = i
                    break
            for item in ignore:
                if item in possible_title:
                    action = "ignore"
                    type = possible_title
                    break

        end_pattern = r"\*\*\*\s+\*\*\*"

        # print(action)

        regulations = self.find_regulations(action=action, type=type.replace("***", ""), text_items=text_items, index=index)
        if regulations:
            print(regulations)

    def convert_pdf_to_txt(self, path):
        start = timer()
        codec = 'utf-8'
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=self.laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        pages = PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True)

        # Analyze first page to get a feel of what's going on
        try:
            first_page = next(pages)
            interpreter.process_page(first_page)
        except StopIteration:
            print("The pdf document may be damaged")
            return

        # Save pages to RAM to interpret only the last 3 ones
        temp_pages = []

        # Get the first page's text
        text = retstr.getvalue()
        num_signature_points = 1
        if 'ΠΕΡΙΕΧΟΜΕΝΑ' in text:
            indexes = re.findall('[0-9] \n', text[120:350])
            num_signature_points = len(indexes)

        for page in pages:
            temp_pages.append(page)

        # Goes through the pages in reverse until if finds the stopword(s)
        signature_points_found = 0
        for page in reversed(temp_pages):
            interpreter.process_page(page)
            current_text = retstr.getvalue()

            if 'Οι Υπουργοί' in current_text or Helper.date_match().findall(current_text) \
                    or 'ΟΙ ΥΠΟΥΡΓΟΙ' in current_text:

                signature_points_found += 1

            if signature_points_found == num_signature_points:
                break

        text = retstr.getvalue()

        fp.close()
        device.close()
        end = timer()
        print("{} seconds elapsed for parsing this pdf's text.".format(end - start))
        return text