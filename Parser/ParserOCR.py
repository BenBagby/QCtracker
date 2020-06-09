from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import tempfile

PDF_file = 'Parser/Input/2500_20040002.pdf'

with tempfile.TemporaryDirectory() as path:
    print(path)

    pages = convert_from_path(PDF_file, output_folder=path)
    image_counter = 1
    for page in pages:
        filename = path+"/page_" + str(image_counter) + ".jpg"
        print(filename)
        page.save(filename, 'JPEG')
        image_counter += 1

    filelimit = image_counter - 1
    outfile = "Parser/Output/out_text.txt"

    f = open(outfile, "a")

    for i in range(1, filelimit + 1):
        filename = path+"/page_"+str(i)+".jpg"
        text = str(pytesseract.image_to_string(Image.open(filename)))
        text = text.replace('-\n', '')
        f.write(text)

    f.close()


