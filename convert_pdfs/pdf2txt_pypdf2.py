import csv, re, os, sys
from timeit import default_timer as timer
import datetime as dt
import PyPDF2


def get_list_files(files_existing):
    Files = list()
    for filename in os.listdir('U:\\tas\\'):
        if filename.endswith('.pdf') and filename not in files_existing:
            Files.append(filename)
        elif filename.endswith('.PDF'):
            filename_4check = filename.replace('PDF','pdf')
            if filename_4check not in files_existing:
                Files.append(filename)
    return Files

#Obtain list of files that are already in your directory
def scan_directory(path2):
    files_existing = []
    for file in os.listdir(path2):
        if file.endswith('.txt'):
            files = file.replace('.txt','.pdf')
            files_existing.append(files)
        else:
            continue
    return files_existing


def convert(filePDF):
    all_pages = []
    pdfFileObj = open(filePDF, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    if pdfReader.isEncrypted:
        print('File is encrypted')
        pages = ["<ENCRYPTED FILE>"]
    else:
        try:
            num_pages = pdfReader.numPages
            print("Document {}; Number of pages {}".format(filePDF,num_pages))
        except PyPDF2.utils.PdfReadError:
            print("PyPDF.ReaderError")
            pages = ["<READER ERROR>"]
            pass
        for pageNum in range(num_pages):
            try:
                pageObj = pdfReader.getPage(pageNum)
                page_content = pageObj.extractText()
                all_pages.append(page_content)
            except IndexError:
                print("File {} has an issue with indexing and pages".format(filePDF))
                pass
            except KeyError:
                print("File {} has an issue with Key error".format(filePDF))
                pass
            except TypeError:
                print("File {} has an issue with Type error and Bytes".format(filePDF))
                pass

    pages =' '.join(x for x in all_pages) #here I can later put a specific delimiter to distinguish between pages!!!!
    return pages

#//////////// main ///////////////////////
#def main():

path1 = '/Home/ubuntu/global-economics/scrape_articles/pdfs_downloaded' #specify pdf files directory
path2 ='/Home/ubuntu/global-economics/convert_pdfs/txt' # specify directory for txt

startTotal = timer()
log = open('Log_{}.txt'.format(str(dt.datetime.today().strftime("%m.%d.%Y"))), 'w')

files_existing = scan_directory(path2)

Files = get_list_files(files_existing)
print(len(Files))

for doc in Files:
    DocStart = timer()
    log.write('Document: {}\n'.format(doc))
    if 'pdf' in doc:
        file = doc.replace('pdf','txt')
    elif 'PDF' in doc:
        file = doc.replace('PDF', 'txt')

    filePDF  = path1 + doc
    fileTXT  = path2 + file
    print("Working with: {}".format(doc))

    print("Text format desired for output detected")
    pages = convert(filePDF)
    fileConverted = open(fileTXT, "w", encoding = 'utf-8')

    fileConverted.write(pages)
    fileConverted.close()
    DocEnd = timer()
    log.write('Time used to convert this document: {} seconds\n'.format(DocEnd - DocStart))
    print("Done with doc: {}\n".format(doc))
