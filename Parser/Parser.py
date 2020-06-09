from pathlib import Path
import PyPDF2





if __name__ == '__main__':
    paths = Path('Input').glob('**/*.pdf')

    for path in paths:
        pdfFileObj = open(path, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

        for pageNum in range(0, pdfReader.numPages):
            pageNum = 2
            pageObj = pdfReader.getPage(pageNum)
            pageContent = pageObj.extractText()
            
            print(pageContent)
        

    