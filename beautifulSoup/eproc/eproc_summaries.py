#!/usr/bin/python

import urllib2
import pymongo
from pymongo import MongoClient
import json
import time
from collections import deque
from bs4 import BeautifulSoup
import errno
import socket
import httplib
import ssl

#connection
def db_connect():
    client = MongoClient('localhost', 27017)
    #set database
    database = client.eproc_research
    return database

#insert into collection summaries
def insert_summaries(summaries, main_url):
    connection = db_connect()
    eproc_summaries_tender = connection.eproc_summaries_tender_2
    status_insert = []
    for summary in summaries:
        try:
            time.sleep(0.2)
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
                "main_url" : main_url, # https://lpse.makassar.go.id/eproc4/lelang/2588234/pengumumanlelang
                "url_detail" : main_url+"eproc4/lelang/"+summary[0]+"/pengumumanlelang",
                "url_peserta" : main_url+"eproc4/lelang/"+summary[0]+"/peserta",
                "url_tahap" : main_url+"eproc4/lelang/"+summary[0]+"/jadwal",
                "url_hasil" : main_url+"eproc4/evaluasi/"+summary[0]+"/hasil",
                "url_pemenang" : main_url+"eproc4/evaluasi/"+summary[0]+"/pemenang",
                "url_pemenangberkontrak" : main_url+"eproc4/evaluasi/"+summary[0]+"/pemenangberkontrak",
            }]
            insert_data = eproc_summaries_tender.insert_many(new_summary)
            if insert_data:
                status_insert.append(1)
            else:
                status_insert.append(0)
        except pymongo.errors.DuplicateKeyError as e:
            status_insert.append(0)
            print "duplicate entry key"
        return status_insert

#url request
def url_req(url):
    string_url = str(url)

    main_url = string_url.split("eproc4",1)[0]

    # request = urllib2.Request(url)
    status_code = 0

    #set connection
    connection = db_connect()
    eproc_url_lists = connection.eproc_url_lists_2

    try:
        time.sleep(0.5)
        print "Get JSON DATA is on process"
        to = 7
        response = urllib2.urlopen(url, timeout=to)
        status_code = response.getcode()

        content = response.read()
        if content:
            try:
                time.sleep(0.2)
                result = json.loads(content)
                if result:
                    if status_code == 200:
                        pass
                        #update status crawl
                        isUpdated = update_status_crawl(main_url,status_code)
                        
                        #insert summaries tender, json data
                        isInserted = insert_summaries(result["data"], main_url)
                        #cek in summaries tender contains false
                        if False in isInserted:
                            return "failed to insert to database"
                        else:
                            return status_code
                else:
                    #failed to serialize json
                    status_code = 997
                    isUpdated = update_status_crawl(main_url,status_code)
            except ValueError:
                #error value
                status_code = 998
                isUpdated = update_status_crawl(main_url,status_code)
        else:
            status_code = 999
            isUpdated = update_status_crawl(main_url,status_code)
    except urllib2.HTTPError as e:
        #error http
        print "error http"
        status_code = 890
        isUpdated = update_status_crawl(main_url,status_code)
    except urllib2.URLError as e:
        print "error url"
        status_code = 891
        isUpdated = update_status_crawl(main_url,status_code)
    except socket.error as e:
        print "error socket"
        status_code = 892
        isUpdated = update_status_crawl(main_url,status_code)
    except httplib.BadStatusLine as e:
        print "bad status line"
        status_code = 893
        isUpdated = update_status_crawl(main_url,status_code)
    except ssl.CertificateError as e:
        print "ssl certificate error"
        status_code = 894
        isUpdated = update_status_crawl(main_url,status_code)
    except httplib.IncompleteRead as e:
        print "error incomplete read"
        status_code = 895
    
    return response.getcode()


#function update status crawl
def update_status_crawl(params,status_code):
    connection = db_connect()
    eproc_url_detail = connection.eproc_url_lists_2
    isUpdated = eproc_url_detail.update_many(
        {"url" : params},
        {"$set" : {
            "status_crawl" : status_code
        }}
    )
    if isUpdated:
        return True
    return False

