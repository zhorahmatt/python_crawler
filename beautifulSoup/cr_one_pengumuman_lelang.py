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
    statusCode = 0
    response = urllib2.urlopen(url).read()
    soup = BeautifulSoup(response, "html.parser")
    return soup

url = "https://lpse.makassar.go.id/eproc4/lelang/2588234/pengumumanlelang"
req = make_soup(url)

mainTable = req.find("table", {"class" : "table-bordered"})
data = {}
result = []
mainTh = mainTable.findAll("th")
connection = make_connection()
eprocDetailTender = connection.eproc_detail_tender
for th in mainTh:
    thData = th.text
    td = th.findNext("td")
    tableOnTd = td.find("table")
    if tableOnTd:
        nestedData = {}
        nestedTh = tableOnTd.findAll("th")
        for nesTh in nestedTh:
            nestedThData = nesTh.text
            print nestedThData
            print "+========================+"
            nestedTd = nesTh.findAll("td")
            print nestedTd
            nestedTdData = nestedTd.text
            nestedData[nestedThData] = nestedTdData
        tdData = nestedData
    else:
        tdData = td.text
    data[thData] = td.text
insertData = eprocDetailTender.insert(data)