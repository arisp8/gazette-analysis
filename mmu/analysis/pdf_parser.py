import os
import io

from subprocess import call
from PIL import Image

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

class CustomPDFParser:

    def __init__(self):
        self.__project_path = os.getcwd()

    def get_pdf_text(self, file_name):
        text = self.convert_pdf_to_txt(self.__project_path + file_name)
        return text

    # Uses libpoppler's pdfimages tool to extract all images from the pdf and then uses PIL to convert from ppm to jpg
    def get_pdf_images(self, file_name, id):
        file_path = self.__project_path + file_name
        directory = self.__project_path + '\\images\\' + str(id)
        images = []
        if not os.path.exists(directory):
            os.makedirs(directory)
            call(['pdfimages', file_path, directory +  "\\" + str(id)])

        files = os.listdir(directory)
        # print(files)
        for file in files:
            image_path = os.path.join(directory, file)
            image = Image.open(image_path)
            image.save(image_path.replace(".ppm", ".jpg"))



        return "YO!"

    def convert_pdf_to_txt(self, path):
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                      password=password,
                                      caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        return text