import os
import re
import io

from subprocess import call
from PIL import Image

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from timeit import default_timer as timer

class CustomPDFParser:

    def __init__(self):
        self.__project_path = os.getcwd()
        # Initialize required objects

        self.retstr = io.StringIO()
        self.laparams = LAParams()
        self.__date_pattern = re.compile(r"\w+,\s+?\d{1,2}\s+?\w+\s+\d{4,4}")

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
        directory = self.__project_path + '\\images\\' + str(id)
        images = []
        if not os.path.exists(directory):
            os.makedirs(directory)
            call(['pdfimages', file_path, directory +  "\\" + str(id)])

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

    def convert_pdf_to_txt(self, path):
        start = timer()
        codec = 'utf-8'
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, self.retstr, codec=codec, laparams=self.laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        pages = PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True)

        # Analyze first page to get a feel of what's going on
        first_page = next(pages)
        interpreter.process_page(first_page)

        # Save pages to RAM to interpret only the last 3 ones
        temp_pages = []

        # Get the first page's text
        text = self.retstr.getvalue()
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
            current_text = self.retstr.getvalue()

            if 'Οι Υπουργοί' in current_text or self.__date_pattern.findall(current_text):
                signature_points_found += 1

            if signature_points_found == num_signature_points:
                break

        text = self.retstr.getvalue()

        fp.close()
        device.close()
        end = timer()
        print("{} seconds elapsed.".format(end - start))
        return text

    def close(self):
        self.retstr.close()