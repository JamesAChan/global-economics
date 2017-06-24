from bs4 import BeautifulSoup
import pdb
soup = BeautifulSoup(open("/Users/jchan/global-economics/convert_pdfs/pdfminer_p3/-doc-cr1701.html"),'html.parser')

row = soup.find_all('div', string='contents')
pdb.set_trace()
for r in row:
    nextSib = r.nextSibling

    pdb.set_trace()
    while nextSib.name != 'div' and nextSib is not None:
        nextSib = nextSib.nextSibling
    print(nextSib.text)
