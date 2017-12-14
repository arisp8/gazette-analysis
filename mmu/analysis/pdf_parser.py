import os
import re
import io

from subprocess import call
from PIL import Image

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextLine
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
        retstr = io.StringIO()
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

    # Analyzes the first page of a pdf document to extract useful info about the laws being analyzed.
    def get_document_info(self, page):
        # This list will contain information regarding all regulations inside the parsed document. Regulations may be:
        # -- Laws
        # -- Presidential Decrees
        # -- Ministerial Decisions
        regulations = []

        # These keywords indicate that the document contains more than one regulation and that they are described in the
        # table of contents.
        multiple = ['ΚΑΝΟΝΙΣΜΟΙ','ΑΠΟΦΑΣΕΙΣ', 'ΠΕΡΙΕΧΟΜΕΝΑ','ΠΡΑΞΕΙΣ ΥΠΟΥΡΓΙΚΟΥ ΣΥΜΒΟΥΛΙΟΥ', 'ΠΡΟΕΔΡΙΚΑ ΔΙΑΤΑΓΜΑΤΑ',
                    'ΑΝΑΚΟΙΝΩΣΕΙΣ', 'AΠΟΦΑΣΕΙΣ']

        # These keywords indicate that the document contains a single regulation of the same type as the keyword
        single =  ['ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ’ ΑΡΙΘΜ.', "ΝΟΜΟΣ ΥΠ’ ΑΡΙΘ.", "ΝΟΜΟΣ ΥΠ’ ΑΡΙθ.", "NOMOΣ ΥΠ’ ΑΡΙΘ.",
                   'ΚΑΝΟΝΙΣΜΟΣ ΥΠ’ ΑΡΙΘΜ.', 'ΝΟΜΟΣ ΥΠ’ ΑΡΙΘΜ.', 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ΄ ΑΡΙΘΜ.', 'NOMOΣ ΥΠ’ ΑΡΙΘΜ.',
                   'NOMOΣ ΥΠ’ ΑΡΙΘM.', 'NOMOΣ ΥΠ΄ΑΡΙΘΜ.', 'ΝΟΜΟΣ ΥΠ’ ΑΡΙΘM.', "ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ ΥΠ' ΑΡΙΘΜ."]

        # These starting titles let us know that the document doesn't contain relevant data.
        ignore = ['ΒΟΥΛΗ ΤΩΝ ΕΛΛΗΝΩΝ', 'ΔΙΟΡΘΩΣΕΙΣ ΣΦΑΛΜΑΤΩΝ']

        multiple_indicator = ""
        text_items = []
        print(page)
        # Get the first 10 textual elements inside the pdf.
        for index, layout_object in enumerate(page):

            if isinstance(layout_object, LTTextBox) or isinstance(layout_object, LTTextLine):
                text = layout_object.get_text()
                text_items.append(text)

            if index == 9:
                break

        found = False
        for possible_title in text_items[4:10]:
            for item in multiple + single + ignore:
                # print(item.lower(), '---', possible_title)
                if item in possible_title:
                    found = True
                    break

        if not found:
            print(text_items)
            # for possible_title in text_items[4:8]:
            #     for item in multiple + single + ignore:
            #         print(item, '---', possible_title)

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