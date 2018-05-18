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
data = dict()
mainTh = mainTable.findAll("th")
for th in mainTh:
    thData = th
    print thData.text
    td = th.findNext("td")
    tdData = td
    print tdData
    print "------------------------------"
    # data[thData] = tdData

# print data
    

