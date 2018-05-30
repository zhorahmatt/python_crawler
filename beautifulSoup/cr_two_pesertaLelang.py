#!/usr/bin/python
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
    eprocUrlDetail = connection.eproc_summaries_tender_2
    strUrl = str(url)
    print url
    soup = ""
    try:
        time.sleep(0.2)
        request = urllib2.urlopen(url)
        print "Crawling is processing....."
        try:
            print "parsing is processing"
            response = request.read()
            soup = BeautifulSoup(response, "html.parser")
            statusCode = 200
            eprocUrlDetail.update_many(
                {"url_detail" : url},
                {"$set" : {
                    "status_crawl" : statusCode
                }}
            )
            return soup
        except socket.error as e:
            errCode = e[0]
            statusCode = 791
            eprocUrlDetail.update_many(
                {"url_detail" : url},
                {"$set" : {
                    "status_crawl" : statusCode
                }}
            )
            return statusCode
        except AttributeError as e:
            errCode = e[0]
            statusCode = 792
            eprocUrlDetail.update_many(
                {"url_detail" : url},
                {"$set" : {
                    "status_crawl" : statusCode
                }}
            )
            return statusCode
    except socket.error as e:
        errCode = e[0]
        statusCode = 892
        eprocUrlDetail.update_many(
            {"url_detail" : url},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except urllib2.HTTPError, e: #handling http error
        statusCode = 890
        eprocUrlDetail.update_many(
            {"url_detail" : url},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except urllib2.URLError, e: #handling url error
        statusCode = 891
        eprocUrlDetail.update_many(
            {"url_detail" : url},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except AttributeError as e:
        errCode = e[0]
        statusCode = 893
        eprocUrlDetail.update_many(
            {"url_detail" : url},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode

def get_url_list(jenis):
    connection = make_connection()
    kode_lelang = connection.eproc_summaries_tender_2
    url_detail = []
    try:
        result = kode_lelang.find({"status_crawl": {"$ne":200}}).limit(200)
        for url in result:
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
    except pymongo.errors.AutoReconnect as e:
        print "gagal koneksi"
        url_detail.append(1)



# url = get_url_list(2)
url = ['https://lpse.makassar.go.id/eproc4/lelang/2608234/peserta']
urlAntrian = deque(url)
while urlAntrian:
    time.sleep(0.5)
    lastUrl = urlAntrian.popleft()
    print lastUrl
    print "===================Crawling Peserta Lelang======================"
    req = make_soup(lastUrl)
    try:
        mainTable = req.find("table", {"class" : "table table-condensed"})
        tbody = mainTable.find("tbody")
        allTr = tbody.findAll("tr")
        peserta = []
        for tr in allTr:
            td = tr.findAll("td")
            peserta.append(td[1].text)
        
        dataPeserta = [{
            "kode_lelang" : 1,
            "peserta" : peserta
        }]
        print dataPeserta
        connection = make_connection()
        eprocTahapTender = connection.eproc_participants_tender
        try:
            # insert data on table peserta lelang
            insertData = eprocTahapTender.insert(dataPeserta)
        except pymongo.errors.DuplicateKeyError as e :
            print "duplicate key"
    except AttributeError as e:
        print "gagal parsing"