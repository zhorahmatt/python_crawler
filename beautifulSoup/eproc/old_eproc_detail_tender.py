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

#set connection
def make_connection():
    client = MongoClient('localhost', 27017)
    database = client.eproc_research
    return database

#crawling data
def make_soup(url):
    connection = make_connection()
    eproc_url_list = connection.eproc_url_lists_2
    
    stringUrl = str(url)
    print "it will be crawl soon"
    soup = ""
    try:
        time.sleep(0.2)
        to = 5 #timeout
        request = urllib2.urlopen(url, timeout=to)
        print "Crawling is processing"
        try:
            time.sleep(0.5)
            response = request.read()
            print "Parsing data is on fire now!!!"
            soup = BeautifulSoup(response, "html.parser")

            status_code = 200
            
            #fungsi update
            isUpdated = update_status_crawl(url, status_code)
            if isUpdated == True:
                return soup
            return isUpdated
        except socket.error as err:
            print "error crawl socket"
            status_code = 501
            isUpdated = update_status_crawl(url, status_code)
            return isUpdated
        except AttributeError as err:
            print "error crawl attribute"
            status_code = 502
            isUpdated = update_status_crawl(url, status_code)
            return isUpdated
    except socket.error as err:
        print "error socket"
        status_code = 503
        isUpdated = update_status_crawl(url, status_code)
        return isUpdated
    except urllib2.HTTPError as e:
        print "error http"
        status_code = 504
        isUpdated = update_status_crawl(url, status_code)
        return isUpdated
    except urllib2.URLError as e:
        print "error url"
        status_code = 505
        isUpdated = update_status_crawl(url, status_code)
        return isUpdated
    except AttributeError as e:
        print "error attribute"
        status_code = 506
        isUpdated = update_status_crawl(url, status_code)
        return isUpdated

#update function
def update_status_crawl(filter, status_code):
    connection = make_connection()
    eproc_url_detail = connection.eproc_summaries_tender_2
    isUpdated = eproc_url_detail.update_many(
        {"url_detail" : filter},
        {"$set" : {
            "status_crawl" : status_code
        }}
    )
    if isUpdated:
        return True
    return False

#get url list function
def get_url_list(tipe, params,limit):
    connection = make_connection()
    eproc_summaries_tender_2 = connection.eproc_summaries_tender_2
    url_detail = []
    try:
        time.sleep(0.2)
        result = eproc_summaries_tender_2.find({"status_crawl": {"$nin": params }}).limit(limit)

        for url in result:
            link = ""
            if tipe == 1:
                #pengumumanlelang
                link = url["url_detail"]
            elif tipe == 2:
                #peserta
                link = url["url_peserta"]
            elif tipe == 3:
                #pemenang
                link = url["url_pemenang"]
            elif tipe == 4:
                #pemenang berkontrak
                link = url["url_pemenangberkontrak"]
            elif tipe == 5:
                #tahap
                link = url["url_tahap"]
            elif tipe == 6:
                #hasil
                link = url["url_hasil"]
            url_detail.append(link)
        return url_detail
    except pymongo.errors.AutoReconnect as err:
        print "gagal koneksi"
        url_detail.append(1)
        return url_detail

#main
tipe = 1
params = [200,600]
limit = 10
urls = get_url_list(tipe, params, limit)
first_queue = deque(urls)
while first_queue:
    time.sleep(0.5)
    this_url = first_queue.popleft()
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print this_url
    try:
        time.sleep(0.2)
        req = make_soup(this_url)
        try:
            time.sleep(0.2)
            main_table = req.find("table",{"class": "table-bordered"})
            data = {}
            main_th = main_table.findAll("th")
            for th in main_th:
                th_data = th.text
                td = th.findNext("td")
                data[th_data] = str(td.contents)
            print "=================================================================================="
            print data
        except AttributeError as e:
            print "gagal parsing 1"
    except AttributeError as e:
        print "gagal parsing 2"