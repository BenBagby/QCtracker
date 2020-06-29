from pathlib import Path
import PyPDF2
import re
from collections import ChainMap

rx_dict = {
    'sample_id': re.compile(r'AnalysisNumber:\s*\S*(?P<value>[0-9]{8}[-][0-9]{3}[A-Z])'),
    'S&W': re.compile(r'Total Sediment and WaterASTM D-4007(?P<value>[0-9.]{4})(?=vol%)'),
}

def find_ext(dr, ext, ig_case=True):
    if ig_case:
        ext = "".join(["[{}]".format(ch + ch.swapcase()) for ch in ext])
    return Path(dr).glob('**/*.'+ext)

def get_pdf_text(PDF_file):

    text_list = []
    pdfFileObj = open(PDF_file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    for pageNum in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(pageNum)
        pageContent = pageObj.extractText()
        text_list.append(pageContent)

    return(text_list)

def parse_page_text(page_text):
    data = []
    for key, rx in rx_dict.items():
        match = rx.search(page_text)
        if match is not None:
            matched_dict = match.groupdict()
            if matched_dict.get('value') is None:
                data.append({key:matched_dict})
            else:
                matched_dict[key] = matched_dict['value'].strip()
            del matched_dict['value']
            data.append(matched_dict)
    page_data = dict(ChainMap(*data))

    return page_data


def get_pdf_data(PDF_file):

    text_list = get_pdf_text(PDF_file)
    print(text_list)

    pdf_data = []
    for page_text in text_list:
        page_data = parse_page_text(page_text)
        if 'S&W' in page_data:
            pdf_data.append(page_data)
    
    return pdf_data

def get_folder_data(folder_path):
    path = find_ext(folder_path,'pdf',ig_case=True)
    folder_data = []
    for PDF_file in path:
        pdf_data = get_pdf_data(PDF_file)
        folder_data.extend(pdf_data)

    return folder_data


if __name__ == '__main__':
    folder_data = get_folder_data('Parser/Temp')
    print(folder_data)