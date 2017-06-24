import time
import requests
from bs4 import BeautifulSoup
import os, sys, csv, re
from timeit import default_timer as timer
import json


def pages_payload(seq, repeated_query):
    payload_new = []
    for x in range(0, seq):
        if x == 0:
            fun_x = "0"
        else:
            fun_x = str(x)+ "00"
        payload = {
            "queryString": repeated_query,
            "queryContext": {"curations": ["ARTICLES", "BLOGS"]},
            "resultContext": {
                "maxResults": "100",
                "offset": fun_x,
                "aspects":["title","lifecycle","location","summary","editorial"]}}
        payload_new.append(payload)
    print(payload_new)
    return payload_new

def create_dict(q1, offset, query_input, l):
    myDict = {}
    myDict['QUERY WORD'] = query_input
    myDict['YEAR'] = str(q1)
    myDict['OFFSET'] = offset
    myDict['ID'] = l['id']
    if l['apiUrl'] is not None:
        myDict['API URL'] = l['apiUrl']
    else:
        myDict['API URL'] = '<missing>'
    myDict['ASPECT'] = l['aspectSet']
    myDict['TITLE'] = l['title']['title']
    myDict['INITIAL_PUB'] = l['lifecycle']['initialPublishDateTime']
    myDict['LAST_PUB'] = l['lifecycle']['lastPublishDateTime']
    myDict['LOCATION'] = l['location']['uri']
    myDict['SUMMARY'] = l['summary']['excerpt']
    try:
        myDict['EDITORIAL'] = l['editorial']['byline']
    except KeyError:
        myDict['EDITORIAL'] = '<missing>'
    return myDict


def query_details(query_input, url, payload_list):
    myListDetailed = []
    i = 1
    q1 = 2007
    for payload in payload_list:
        repeated_query = payload['queryString']
        time.sleep(3)
        r = requests.post(url, data=json.dumps(payload))
        if r.status_code == 200:
            print("Initial Page responded {}".format(str(i)))
            load = r.json()
            data = load['results']
            indexNumber = int(''.join([str(d['indexCount']) for d in data]))
            seq = int(indexNumber/99) +1
            print("Number of hits: {}".format(str(indexNumber)))
            if indexNumber > 0:
                if seq < 2:
                    offset = '0'
                    new_list = [dt['results'] for dt in data]
                    NewList = [item for sublist in new_list for item in sublist]
                    for l in NewList:
                        myDict = create_dict(q1, offset, query_input, l)
                        myListDetailed.append(myDict)
                    i += 1
                    q1 += 1
                else:
                    print('Number of pages:{}'.format(str(seq)))
                    payload_new = pages_payload(seq, repeated_query)
                    for new in payload_new:
                        offset = new['resultContext']['offset']
                        print("Page: {}".format(offset))
                        time.sleep(1)
                        rq = requests.post(url, data=json.dumps(new))
                        if rq.status_code == 200:
                            load1 = rq.json()
                            data1 = load1['results']
                            new_list1 = [dt['results'] for dt in data1]
                            NewList1 = [item for sublist in new_list1 for item in sublist]
                            print("Page: {} NewList: {}".format(offset, len(NewList1)))
                            for l in NewList1:
                                myDict = create_dict(q1, offset,query_input, l)
                                myListDetailed.append(myDict)
                        else:
                            print('PROBLEM -  Status Code: {}'.format(rq.status_code))
                    print("Done with pages iterations for {}".format(q1))
                    i += 1
                    q1 += 1
            else:
                print("No matches for year: {}".format(str(q1)))
                i += 1
                q1 += 1     
                continue
        else:
            print("PROBLEM: {}".format(r.status_code))
            i += 1
            q1 += 1
            continue
    return myListDetailed


def create_query(qString):
#def create_query():    
    list_start = []
    for i in range(7, 17):
        bdate = 'lastPublishDateTime:>'
        date = str(i)
        if len(date) == 1:
            begin = bdate + '200' + date + '-01-01T00:00:00Z'
            list_start.append(begin)
        else:
            begin = bdate + '20' + date + '-01-01T00:00:00Z'
            list_start.append(begin)
    list_end = []
    for i in range(8, 18):
        edate = 'lastPublishDateTime:<'
        date = str(i)
        if len(date) == 1:
            end = edate + '200' + date + '-01-01T00:00:00Z)'
            list_end.append(end)
        else:
            end = edate + '20' + date + '-01-01T00:00:00Z)'
            list_end.append(end)
    query_list = []
    zipped = zip(list_start, list_end)
    for a,b in zipped:
        #newURL = a + " AND " + b
        newURL = qString + a + " AND " + b
        query_list.append(newURL)
    #print(query_list)
    return query_list

def create_payload(query_list):
    payload_list = []
    for elm in query_list:
        payload = {
            "queryString": elm,
            "queryContext": {"curations": ["ARTICLES", "BLOGS"]},
            "resultContext": {"maxResults": "100", "offset": "0", "aspects":["title","lifecycle","location","summary","editorial"]}}
        payload_list.append(payload)
    return payload_list

####################################################################
def main():
    outdir = 'C:\\User\\.....' #your directory
#################################   TYPE QUERY BELOW   ################## 
    query_input = 'fiscal AND (" VAT " OR "value-added tax" OR "value-added taxation" OR "value-added taxes")'
##################################################################################   
    qString = "(" + query_input + ") AND ("
    url = 'http://api.ft.com/content/search/v1?apiKey=YOUR_API_KEY_HERE' #API KEY 
    query_list = create_query(qString)
    payload_list = create_payload(query_list)
    myListDetailed = query_details(query_input,url, payload_list)
    detail_key = myListDetailed[0].keys()
    #Change name of the file below
    with open(os.path.join(outdir, '-DETAILS-fiscal_AND_inequality.csv'), 'w', newline ='', encoding = 'utf-8') as output_file:
        writer = csv.DictWriter(output_file, detail_key)
        writer.writeheader()
        writer.writerows(myListDetailed)
        output_file.close()
        
if __name__ == "__main__":
    print(main())
