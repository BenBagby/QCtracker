from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import tempfile
from pathlib import Path
import PyPDF2
import re
from collections import ChainMap

#for testing
import sqlite3
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta


rx_dict = {
    'sample_id': re.compile(r'CERTIFICATE OF ANALYSIS\s*(?P<value>[0-9]{8}[-][0-9]{3}[A-Z])'),
    'location': re.compile(r'Well\s*:\s*(?P<value>[\S\s]*?)(?=\sSample Psig| \/ )'),
    'sample_date': re.compile(r'Sample Date\/Time:\s*(?P<value>\d{1,2}\/\d{1,2}\/\d{4})'),
    'shrinkage': re.compile(r'Shrinkage Factor\s*(?P<value>[0-9.]*)'),
    'gor': re.compile(r'Flash Factor\s*(?P<value>[0-9.]*)')
}

def find_ext(dr, ext, ig_case=True):
    if ig_case:
        ext = "".join(["[{}]".format(ch + ch.swapcase()) for ch in ext])
    return Path(dr).glob('**/*.'+ext)


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
        pages = convert_from_path(PDF_file, output_folder=path, thread_count=10)
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
    page_num_list = get_img_page_numbers(PDF_file)

    text_list = get_pdf_text(PDF_file, page_num_list)

    pdf_data = []
    for page_text in text_list:
        page_data = parse_page_text(page_text)
        if 'shrinkage' in page_data:
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
    folder_data = get_folder_data('Parser/Input')
    print(folder_data)
    
    
    
    '''
    conn = sqlite3.connect('database copy 2.db')
    cursor = conn.cursor()
    
    sql_imp = "SELECT * from shrinkage WHERE location=? AND status NOT LIKE ?"
    folder_data_calc = []
    for data in folder_data:
        cursor.execute(sql_imp,(data['location'],'%'+'exclude'+'%'))
        names = [x[0] for x in cursor.description]
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=names)
        df = df.append(data,ignore_index = True)

        df['sample_date'] =pd.to_datetime(df.sample_date)
        df = df.sort_values(by='sample_date')
        df.reset_index(drop=True, inplace = True)
        df['status'] = df['status'].astype(str)

        df['status'].replace('nan', 'empty', regex = True, inplace = True)
        current_date = pd.to_datetime(data['sample_date'])

        time_series = pd.to_datetime(df['sample_date'])
        day1_time_series = time_series.apply(lambda dt: dt.replace(day = 1))
        filter3 =  day1_time_series >= (current_date + relativedelta(months=-6)).replace(day = 1)
        filter4 = time_series < current_date
        reduced_df = df.where(  pd.Series(filter3) & pd.Series(filter4) ) 
        
        applied_average = reduced_df['shrinkage'].astype(float).mean()
        lower_limit = applied_average * (1 - 0.04)
        upper_limit = applied_average * (1 + 0.04)

        if lower_limit <= float(data['shrinkage']) <= upper_limit:
            status = 'pass'
        else:
            status = 'fail(exclude)'

        #df = df.set_index('sample_id')
        #df.at[data['sample_id'], 'applied_average'] = rolling_mean2
        
        data.update({'applied_average':applied_average, 'lower_limit':lower_limit, 'upper_limit':upper_limit, 'status':status})

        folder_data_calc.append(data)
    print(folder_data_calc)
    '''
    

      




