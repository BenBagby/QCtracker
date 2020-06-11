from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import tempfile
from pathlib import Path
import PyPDF2

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
        print(text_list)