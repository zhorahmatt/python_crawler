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

#insert to database
def insert_data(summaries, mainUrl):
    connection = db_connect()
    #set collection
    con_eproc_summaries_tender = connection.eproc_summaries_tender_2
    statusInsert = []
    for summary in summaries:
        try:
            insert_summary = [{
                "kode_lelang" : summary[0],
                "nama_lelang" : summary[1],
                "instansi" : summary[2],
                "tahap_lelang" : summary[3],
                "nilai_pagu_paket" : summary[4],
                "metode_kualifikasi" : summary[5],
                "metode_dokumen" : summary[5],
                "metode_pengadaan" : summary[6],
                "metode_evaluasi" : summary[7],
                "kategori" : summary[8],
                "main_url" : mainUrl
            }]

            insert_data = con_eproc_summaries_tender.insert_many(insert_summary)
            if insert_data:
                statusInsert.append(1)
                print "Success inserting data"
            else:
                statusInsert.append(0)
                print "Failed inserting data"
        except pymongo.errors.DuplicateKeyError as e:
            statusInsert.append(0)
            print "Duplicate Entry Key"
    return statusInsert

#get all url list
def get_url_list_from_db():
    connection = db_connect()
    con_eproc_url_list = connection.eproc_url_lists_2
    urls = []
    for url in con_eproc_url_list.find({"status_crawl" : {"$ne" : 200}}):
        link_to_check = url["url"]+"eproc4/dt/lelang"
        urls.append(link_to_check)
    return urls

def make_request(this_url):
    string_url = str(this_url)
    main_url = string_url.split("eproc4",1)[0]
    statusCode = 0
    
    #set connection
    connection = db_connect()
    con_eproc_url_list = connection.eproc_url_lists_2

    #request
    try:
        time.sleep(1)
        print "on processing"
        response = urllib2.urlopen(this_url)
        
        status_code = response.getcode()
        print status_code
        
        content = response.read()
        time.sleep(0.5)
        if content:
            pass
        else:
            #could not read the content
            status_code = 999
            #update to database
    except Exception as identifier:
        pass

#update data
def update_data(collection,filter, data):
    connection = db_connect()


#main
set_url = "https://lpse.acehprov.go.id/eproc4/dt/lelang"