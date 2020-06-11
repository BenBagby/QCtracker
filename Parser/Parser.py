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


if __name__ == '__main__':
    
    path = Path('Parser/Input').glob('**/*.pdf')
    for PDF_file in path:
        page_num_list = get_img_page_numbers(PDF_file)
        print(page_num_list)

        

    