import os
import io
import sys

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator, PDFConverter
from pdfminer.layout import LAParams, LTImage, LTPage, LTFigure, LTRect
from pdfminer.pdfpage import PDFPage
from binascii import b2a_hex

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

class CustomPDFParser:

    images_folder = os.getcwd() + "\\images\\"

    def __init__(self):
        self.__project_path = os.getcwd()

    def get_raw_data(self, file_name):
        file_path = self.__project_path + file_name
        data = self.convert_pdf_to_txt(file_path)

    def parse_layout_objects(self, lt_objects, page_number, text_content = []):

        text_content = []

        for lt_obj in lt_objects:
            if isinstance(lt_obj, LTFigure):
                text_content.append(self.parse_layout_objects(lt_obj._objs, page_number, text_content))
            elif isinstance(lt_obj, LTImage):
                # an image, so save it to the designated folder, and note it's place in the text
                saved_file = self.save_image(lt_obj, page_number, self.images_folder)
                if saved_file:
                    text_content.append("[Image: " + os.path.join(self.images_folder, saved_file) + "]")
                else:
                    print(sys.stderr, "Error saving image on page", page_number, lt_obj.__repr__)

        return '\n'.join(text_content)

    def save_image(self, lt_image, page_number, images_folder):

        result = None


        if lt_image.stream:
            file_stream = lt_image.stream.get_rawdata()
            file_ext = self.determine_image_type(file_stream[0:4])

            if file_ext:
                file_name = ''.join([str(page_number), '_', lt_image.name, file_ext])
                if self.write_file(images_folder, file_name, lt_image.stream.get_rawdata(), flags='wb'):
                    result = file_name

        return result

    def determine_image_type(self, stream_first_4_bytes):
        """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
        file_type = None
        bytes_as_hex = b2a_hex(stream_first_4_bytes)
        print(bytes_as_hex)
        if bytes_as_hex.startswith(b'ffd8'):
            file_type = '.jpeg'
        elif bytes_as_hex == '89504e47':
            file_type = '.png'
        elif bytes_as_hex == '47494638':
            file_type = '.gif'
        elif bytes_as_hex.startswith(b'424d'):
            file_type = '.bmp'
        return file_type

    def write_file(self, folder, filename, filedata, flags='w'):
        result = False
        if os.path.isdir(folder):
            try:
                file_obj = open(os.path.join(folder, filename), flags)
                # print(filedata)
                file_obj.write(filedata)
                file_obj.close()
                result = True
            except IOError:
                pass
        return result

    def convert_pdf_to_txt(self, path):

        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        aggregator = PDFPageAggregator(rsrcmgr, laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, aggregator)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        text_content = []

        pages = PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True)

        for page_num, page in enumerate(pages):
            interpreter.process_page(page)
            layout = aggregator.get_result()
            text_content.append(self.parse_layout_objects(layout, page_num+1))

        fp.close()
        device.close()
        retstr.close()
        return text_content