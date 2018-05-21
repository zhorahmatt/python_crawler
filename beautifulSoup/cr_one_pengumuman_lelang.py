import urllib2
import pymongo
from pymongo import MongoClient
import json
import time
from collections import deque
from bs4 import BeautifulSoup
from collections import deque
import errno
import socket
import httplib
import ssl

def make_connection():
    client = MongoClient('localhost', 27017)
    database = client.eproc_research
    return database

def make_soup(url):
    connection = make_connection()
    eprocUrlList = connection.eproc_url_lists_2
    strUrl = str(url)
    mainUrl = strUrl.split("eproc4",1)[0]
    try:
        time.sleep(0.2)
        request = urllib2.urlopen(url)
        print "Crawling is on process....."
        try:
            response = request.read()
            soup = BeautifulSoup(response, "html.parser")
            return soup
        except socket.error as e:
            errCode = e[0]
            statusCode = 892
            eprocUrlList.update_many(
                {"url" : mainUrl},
                {"$set" : {
                    "status_crawl" : statusCode
                }}
            )
    except socket.error as e:
        errCode = e[0]
        statusCode = 892
        eprocUrlList.update_many(
            {"url" : mainUrl},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )

def get_url_list(jenis):
    connection = make_connection()
    kode_lelang = connection.eproc_summaries_tender_2
    url_detail = []
    for url in kode_lelang.find():
        link = ""
        if jenis == 1:
            #pengumumanlelang
            link = url["url_detail"]
        elif jenis == 2:
            #peserta
            link = url["url_peserta"]
        elif jenis == 3:
            #pemenang
            link = url["url_pemenang"]
        elif jenis == 4:
            #pemenang berkontrak
            link = url["url_pemenangberkontrak"]
        elif jenis == 5:
            #tahap
            link = url["url_tahap"]
        elif jenis == 6:
            #hasil
            link = url["url_hasil"]
        url_detail.append(link)
    return url_detail



url = get_url_list(1)
urlAntrian = deque(url)
while urlAntrian:
    time.sleep(0.5)
    lastUrl = urlAntrian.popleft()
    print lastUrl
    print "================================"
    req = make_soup(lastUrl)
    mainTable = req.find("table", {"class" : "table-bordered"})
    data = {}
    mainTh = mainTable.findAll("th")
    connection = make_connection()
    eprocDetailTender = connection.eproc_detail_tender
    for th in mainTh:
        thData = th.text
        td = th.findNext("td")
        # tableOnTd = td.find("table")
        # if tableOnTd:
        #     nestedData = {}
        #     nestedTh = tableOnTd.findAll("th")
        #     for nesTh in nestedTh:
        #         nestedThData = nesTh.text
        #         print nestedThData
        #         print "+========================+"
        #         nestedTd = nesTh.findAll("td")
        #         print nestedTd
        #         nestedTdData = nestedTd.text
        #         nestedData[nestedThData] = nestedTdData
        #     tdData = nestedData
        # else:
        #     tdData = td.text
        data[thData] = str(td)
    insertData = eprocDetailTender.insert(data)