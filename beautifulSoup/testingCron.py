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
    strUrl = str(url)
    mainUrl = strUrl.split("eproc4",1)[0]
    request = urllib2.Request(url)
    statusCode = 0
    connection = make_connection()
    eprocUrlList = connection.eproc_url_lists_2
    try:
        time.sleep(1)
        print "on process"
        TO = 4
        response = urllib2.urlopen(url, timeout=TO)
        statusCode = response.getcode()
        print statusCode
        content = response.read()
        time.sleep(0.5)
        if content:
            #serialize to json
            try:
                time.sleep(0.5)
                result = json.loads(content)
                if result:
                    #update eproc url lists
                    if statusCode == 200:
                        eprocUrlList.update_many(
                            {"url" : mainUrl},
                            {"$set" : {
                                "status_crawl" : statusCode
                            }}
                        )
                        summariesTender = insert_summaries_tender_to_db(result["data"],mainUrl)
                        if False in summariesTender:
                            return "gagal simpan di database"
                        else:
                            return statusCode
                else:
                    statusCode = 997
                    eprocUrlList.update_many(
                        {"url" : mainUrl},
                        {"$set" : {
                            "status_crawl" : statusCode
                        }}
                    )
                    return statusCode
            except ValueError:
                statusCode = 998
                eprocUrlList.update_many(
                    {"url" : mainUrl},
                    {"$set" : {
                        "status_crawl" : statusCode
                    }}
                )
                return statusCode
        else:
            statusCode = 999
            eprocUrlList.update_many(
                {"url" : mainUrl},
                {"$set" : {
                    "status_crawl" : statusCode
                }}
            )
    except urllib2.HTTPError, e: #handling http error
        statusCode = 890
        eprocUrlList.update_many(
            {"url" : mainUrl},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except urllib2.URLError, e: #handling url error
        statusCode = 891
        eprocUrlList.update_many(
            {"url" : mainUrl},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except socket.error as e: #handling socket error
        errCode = e[0]
        statusCode = 892
        eprocUrlList.update_many(
            {"url" : mainUrl},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except httplib.BadStatusLine as e: #handling bad status line
        statusCode = 893
        eprocUrlList.update_many(
            {"url" : mainUrl},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except ssl.CertificateError as e: #handling error ssl
        statusCode = 894
        eprocUrlList.update_many(
            {"url" : mainUrl},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    except httplib.IncompleteRead as e:
        statusCode = 895
        eprocUrlList.update_many(
            {"url" : mainUrl},
            {"$set" : {
                "status_crawl" : statusCode
            }}
        )
        return statusCode
    return response.getcode()

def get_url_from_db():
    mongo_db = make_connection()
    url_lists = mongo_db.eproc_url_lists_2
    all_url = []
    for url in url_lists.find({"url" : "http://180.250.49.210/"}):
        link_to_check = url["url"]+"eproc4/dt/lelang"
        all_url.append(link_to_check)
    return all_url

def url_checker():
    all_url = get_url_from_db()
    limit = 10
    list_queue = []
    for url in all_url:
        if(len(list_queue) < 11):
            list_queue.append(url)
    return list_queue

def updateData(collection, filter, data):
    connection = make_connection()
    eprocCollection = connection.collection
    update = eprocCollection.update_many(
        {"url" : filter},
        {"$set" : {
            "status_crawl" : data
        }}
    )
    return update

def insert_summaries_tender_to_db(summaries, mainUrl):
    connection = make_connection()
    eprocSummariesTender = connection.eproc_summaries_tender_2
    statusInsert = []
    for summary in summaries:
        try:
            new_summary = [{
                "kode_lelang"   : int(summary[0]),
                "nama_lelang"   : summary[1],
                "instansi"  : summary[2],
                "tahap_lelang"  : summary[3],
                "nilai_pagu_paket"  : summary[4],
                "metode_kualifikasi"    : summary[5], #lakukan pemisahan kata
                "metode_dokumen"    : summary[5], #lakukan pemisahan kata
                "metode_pengadaan"  : summary[6],
                "metode_evaluasi"   : summary[7],
                "kategori"  : summary[8],
                "main_url" : mainUrl, # https://lpse.makassar.go.id/eproc4/lelang/2588234/pengumumanlelang
                "url_detail" : mainUrl+"eproc4/lelang/"+summary[0]+"/pengumumanlelang",
                "url_peserta" : mainUrl+"eproc4/lelang/"+summary[0]+"/peserta",
                "url_tahap" : mainUrl+"eproc4/lelang/"+summary[0]+"/jadwal",
                "url_hasil" : mainUrl+"eproc4/evaluasi/"+summary[0]+"/hasil",
                "url_pemenang" : mainUrl+"eproc4/evaluasi/"+summary[0]+"/pemenang",
                "url_pemenangberkontrak" : mainUrl+"eproc4/evaluasi/"+summary[0]+"/pemenangberkontrak",
            }]
            insert_data = eprocSummariesTender.insert_many(new_summary)
            if insert_data:
                statusInsert.append(1)
            else:
                statusInsert.append(0)
        except pymongo.errors.DuplicateKeyError as e:
            statusInsert.append(0)
            print "Duplicate Entry Key"
    return statusInsert


dummy = get_url_from_db()
antrian = deque(dummy) #using queue
newAntrian = deque([])
while antrian:
    time.sleep(0.5)
    last = antrian.popleft()
    print last
    req = make_soup(last)
    if req == 200:
        print str(req)+" status code -- load data dari "+last
    else:
        newAntrian.append(last)
        print str(req)+" status code -- load data dari "+last
print antrian

#masukkan ke antrian baru untuk diproses
print newAntrian
lastAntrian = deque([])
while newAntrian:
    time.sleep(0.5)
    last = newAntrian.popleft()
    print last
    req = make_soup(last)
    if req == 200:
        print str(req)+" status code -- load data dari "+last
    else:
        lastAntrian.append(last)
        print str(req)+" status code -- load data dari "+last

print lastAntrian
#save ke database