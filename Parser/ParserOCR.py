from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import tempfile

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
            text_list.append(text)

    return(text_list)

if __name__ == '__main__':
    PDF_file = 'Parser/Input/2500_20040002.pdf'
    page_num_list = [3, 8, 13]
    text_list = get_pdf_text(PDF_file, page_num_list)
    print(text_list)