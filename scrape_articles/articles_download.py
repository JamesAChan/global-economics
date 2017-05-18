from bs4 import BeautifulSoupimport os, csv, sys, reimport requestsimport datetime as dtfrom timeit import default_timer as timer#Obtain list of files that are already in your directorydef scan_directory(dirout):    files_existing = [file.replace('.pdf','') for file in os.listdir(dirout) if file.endswith('.pdf')]    return files_existing#Configure search parametersdef config(chunk1):    dictQ = {             'query_word': 'Article+IV', #search term             'when': 'After', #options: After, Before, During             'year':'2015' # year(s) of interest             }    query_string = chunk1 + 'title=' + dictQ['query_word'] + '&when='+dictQ['when']+'&year='+dictQ['year']    return query_string       #Obtain number of total pages to iterate throughdef get_total_page(query_string):    a=requests.get(query_string)    if a.status_code == 200:        print('Main page responded')        soup = BeautifulSoup(a.text, 'html.parser')        docs_string = soup.find('p',{'class':'resultsdoc'}).text.strip()        docs = re.sub('\s+','', docs_string)        docs2 = re.search(r'(?<=found)\d{1,5}', docs)        docs_number = int(docs2.group(0))        pages_string = soup.find('p', {'class': 'pages'}).text.strip()        pages = re.sub('\s+',' ', pages_string)        pages2 = re.search(r'(?<=of\s)\d{1,4}(?=\s1)', pages)        pages_number = int(pages2.group(0))    else:        print('WARNING {}\n'.format(a.status_code))    return docs_number, pages_number#Forms list of all queries for all pagesdef form_queries(query_string, pages_number):    list_queries = []    for i in range(pages_number):        new_query = query_string + '&page=' + str(i+1)        list_queries.append(new_query)    return list_queries#Scrape list of pdf (.ashx) links + some metadata - produces CSV file with summary information for each documentdef document_pages(dirout,chunk2,list_queries,query_string):    text_comp = re.compile(r'Series', re.DOTALL)    series_comp = re.compile(r'(?<=Series:).*')    fname_comp = re.compile(r'(?<=\/)\w{2,6}\d{3,7}(?=.ashx)')    size_comp = re.compile(r'(?<=is\s)\d{1,100000}.{3}')    pubtxt_comp = re.compile(r'(?<=Date:).*')    myList = []    for each in list_queries:        r = requests.get(each)        if r.status_code == 200:            print('Good request {}'.format(each))        s = BeautifulSoup(r.text, 'html.parser')        div1 = s.find_all('div', {'class':'result-row pub-row'})        for d in div1:            try:                link_chunk = d.find('h6').find('a')['href']            except AttributeError:                link_chunk = '<none>'            full_link = chunk2 + link_chunk            try:                author = d.find('p',{'class':'author'}).find('a').text            except AttributeError:                author = '<none>'                continue            try:                series = d.find('strong', text= text_comp).parent.text                series_text = series_comp.search(series)                series_out = series_text.group(0).strip()            except AttributeError:                series_out = '<none>'            try:                pubdates = d.find('strong',text=re.compile(r'Date', re.DOTALL)).parent.text                pub_text = pubtxt_comp.search(pubdates)                pub_out = pub_text.group(0).strip()            except AttributeError:                pub_out ='<none>'                continue            try:                subject = d.find('span',{'class':'subj'}).find_all('a')                sub_out = [s.text.strip() for s in subject]                #sub_out = []                #for s in subject:                    #sub_out.append(s.text.strip())            except AttributeError:                sub_out = '<none>'                continue            req = requests.get(full_link)            if req.status_code == 200:                soup2 = BeautifulSoup(req.text, 'html.parser')                info_chunk = soup2.find_all(lambda tag: tag.name == 'p' and tag.get('class') == ['pub-desc'])                try:                    l_chunk = info_chunk[0].find('a')['href']                    if l_chunk.endswith('.ashx'):                        pdf_link = chunk2 + l_chunk                        try:                            fname = fname_comp.search(l_chunk)                            filename = fname.group(0)                        except AttributeError:                            print('REGEX WARNING {}\n'.format(sys.exc_info()[0]))                            raise                        try:                            size_text = soup2.find('span',{'class':'pdf-info'}).text                            size_regex = size_comp.search(size_text)                            size_value = size_regex.group(0)                            descript = info_chunk[1].text                        except:                            size_value = '<none>'                            continue                except TypeError:                    l_chunk = '<none>'                    pdf_link = '<none>'                    filename = '<none>'                    continue            else:                print('WARNING: {}\n'.format(full_link))                continue            myDict = {                      'QueryPage': each,                      'PageLink': full_link,                      'PDFLink': pdf_link,                      'PDFSize': size_value,                      'Author': author,                      'Series': series_out,                      'PublicationDate': pub_out,                      'Description':descript,                      'Subject': sub_out,                      'Filename': filename                      }            myList.append(myDict)            print("div + 1")    keys = myList[0].keys()    with open(os.path.join(dirout,'summary_tables_2000.csv'), 'w', newline='', encoding ='utf-8') as csvfile:        writer = csv.DictWriter(csvfile, keys)        writer.writeheader()        writer.writerows(myList)        csvfile.close()    print('Finished printing summary table\n')    return myListdef download_locally(myList,files_existing,log,dirout):    #Alternatives? new_names = [item['Filename'] for item in myList if item['Filename'] not in files_existing]    #Alternatives? new_links = [item['PDFLink'] for item in myList if item['Filename'] not in files_existing]    new_names = []    new_links = []    for item in myList:        filename = item['Filename']        if filename not in files_existing:            new_names.append(filename)            new_links.append(item['PDFLink'])    new_zip = list(zip(new_names, new_links))    log.write("Total NEW documents found: {}\n".format(len(new_links)))    print('Total NEW documents found: {}\n'.format(len(new_links)))    if len(new_zip)>0:        for a, b in new_zip:            q = requests.get(b)            if q.status_code == 200:                    with open(os.path.join(dirout,'-doc-' + str(a) +'.pdf'), 'wb') as f:                        f.write(q.content)                        f.close()                    log.write('Finished loading: -doc-{}.pdf\n'.format(a))            else:                print('WARNING: {}\n'.format(q.status_code))    else:        log.write("No new files to save\n")        print("No new files to save\n")    finished = "Finished downloading locally"    return finished##############################################################def main():    dirout = '/Users/jchan/global-economics/data' #Change to directory for PDF files if you want them locally stored    chunk1 = 'http://www.imf.org/en/Publications/Search?'    chunk2 = 'http://www.imf.org'    startTotal = timer()    os.chdir('/Users/jchan/global-economics/log') #Change to directory you want your log output    log = open('Log_{}.txt'.format(str(dt.datetime.today().strftime("%m.%d.%Y"))), 'w')    files_existing = scan_directory(dirout)    query_string = config(chunk1)    log.write('Query: {}\n'.format(query_string))    docs_number, pages_number = get_total_page(query_string)    print('Total Number of pages found: {}\n'.format(str(pages_number)))    log.write('Total Number of pages to scan: {}\n'.format(str(pages_number)))    log.write('Total Number of documents found: {}\n'.format(str(docs_number)))    print('Total Number of documents found: {}\n'.format(str(docs_number)))    list_queries = form_queries(query_string, pages_number)    myList = document_pages(dirout,chunk2,list_queries,query_string)    #finished = download_locally(myList,files_existing,log, dirout) Uncomment if you also want to store files locally    endTotal = timer()    log.write('Time used for parsing: {} seconds'.format(endTotal - startTotal))    #print('Time used for parsing: {} seconds'.format(endTotal - startTotal))    log.close()if __name__ == '__main__':    #print('test')    main()