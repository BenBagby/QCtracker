from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import tempfile
from pathlib import Path
import PyPDF2
import re

rx_dict = {
    'Sample Number': re.compile(r'CERTIFICATE OF ANALYSIS\s*(?P<value>[0-9]{8}[-][0-9]{3}[A-Z])'),
    'Location': re.compile(r'Well\s*:\s*(?P<value>[\S\s]*)(?=\sSample Psig)'),
    'Sample Date': re.compile(r'Sample Date\/Time:\s*(?P<value>\d{1,2}\/\d{1,2}\/\d{4})'),
    'Shrinkage Factor': re.compile(r'Shrinkage Factor\s*(?P<value>[0-9.]*)'),
    'GOR': re.compile(r'Flash Facto\s*(?P<value>[0-9.]*)'),
    'blank': re.compile(r'zzzzzzzzzzzz\s*(?P<value>[0-9.]*)')
}


def get_img_page_numbers(PDF_file):

    pdfFileObj = open(PDF_file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    page_num_list = []
    for pageNum in range(0, pdfReader.numPages):

        pageObj = pdfReader.getPage(pageNum)
        pageContent = pageObj.extractText()
        if len(pageContent) < 50:
            page_num_list.append(pageNum)

    return page_num_list

def get_pdf_text(PDF_file, page_num_list):

    with tempfile.TemporaryDirectory() as path:
        pages = convert_from_path(PDF_file, output_folder=path)
        image_counter = 1

        for page in pages:
            filename = path+"/page_" + str(image_counter) + ".jpg"
            page.save(filename, 'JPEG')
            image_counter += 1

        text_list = []
        for i in page_num_list:
            filename = path+"/page_"+str(i)+".jpg"
            text = str(pytesseract.image_to_string(Image.open(filename)))
            text = text.replace('-\n', '')
            text = text.replace('\n', ' ')
            text_list.append(text)

    return(text_list)

if __name__ == '__main__':
    path = Path('Parser/Input').glob('**/*.pdf')
    for PDF_file in path:
        page_num_list = get_img_page_numbers(PDF_file)
        print(page_num_list)

        text_list = get_pdf_text(PDF_file, page_num_list)
        print(text_list[3])

        data = []
        for key, rx in rx_dict.items():
            match = rx.search(text_list[4])
            if match is not None:
                print(match.groupdict())