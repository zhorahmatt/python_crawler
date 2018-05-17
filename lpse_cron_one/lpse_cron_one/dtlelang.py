import urllib2
import json
import pymongo
from pymongo import MongoClient
import pprint
from collections import deque
import time
from bs4 import BeautifulSoup

def db_connection():
    client = MongoClient('localhost', 27017)
    database = client.eproc_research
    return database

def get_url_list():
    is_database = db_connection()
    mongo_lpse_url_list =  is_database.eproc_url_lists

    urls = []
    ids = []
    #append url list to urls var
    for mongo_url in mongo_lpse_url_list.find():
        link_summary = mongo_url["url"]+"eproc4/dt/lelang"
        urls.append(link_summary)
        ids.append(mongo_url["_id"])

    #link_summary = "https://lpse.acehprov.go.id/eproc4/dt/lelang"
    return urls, ids

def httpReq():
    urls, ids = get_url_list()
    
    lists = []
    eDatabase = db_connection()
    success_data = eDatabase.eproc_url_lists
    for id,list in enumerate(urls):
        #error handling
        time.sleep(2)
        try:
            response = urllib2.urlopen(list)
            bulk_data = response.read()
            #decode result.
            result = json.loads(bulk_data)
            time.sleep(0.1)
            response.close()

            insert_data = insert_to_database(result["data"])
            if insert_data:
                success_data = eDatabase.eproc_url_lists
                success_data.update_many(
                    {"_id" : ids[id]},
                    {"$set" : {
                        "status_url" : 0 #berhasil value = 0
                    }
                    }
                )
                lists = True
            else:
                lists = False
        except urllib2.URLError as e:
            #save ke database errornya
            error_data = eDatabase.eproc_url_lists
            error_data.update_many(
                {"_id" : ids[id]},
                {"$set" : {
                    "status_url" : 1.0
                }}
            )
    return lists

def insert_to_database(summaries):
    db = db_connection()
    mongo_lpse_summaries_tender = db.eproc_summaries_tender
    status_insert = []
    for summary in summaries:
        new_summary = [{
            "kode_lelang"   : summary[0],
            "nama_lelang"   : summary[1],
            "instansi"  : summary[2],
            "tahap_lelang"  : summary[3],
            "nilai_pagu_paket"  : summary[4],
            "metode_kualifikasi"    : summary[5], #lakukan pemisahan kata
            "metode_dokumen"    : summary[5], #lakukan pemisahan kata
            "metode_pengadaan"  : summary[6],
            "metode_evaluasi"   : summary[7],
            "kategori"  : summary[8],
        }]
        insert_data = mongo_lpse_summaries_tender.insert_many(new_summary)
        if insert_data == True:
            status_insert.append(1)
        status_insert.append(0)
    
    status = False
    if status in status_insert:
        return True

def testing():
    urls, ids = get_url_list()
    database = db_connection()
    url_mongo_list = database.eproc_url_lists
    
    status = []
    for id in ids:
        stat = url_mongo_list.find_one({"_id" : id})
        status.append(stat)
    return status

#get json data from dt/lelang
def crawl_summaries_tender():
    urls, ids = get_url_list()


    #
    limit = 10
    
#main
#anjay = httpReq()
#print anjay


#queue class using list
class Queue:
    def __init__(self):
        self.queue = list()

    #mengisi data ke queue
    def enqueue(self,data):
        if data not in self.queue:
            self.queue.insert(0,data)
            return True
        return False
    
    #hapus data ke queue
    def dequeue(self):
        if len(self.queue) > 0:
            return self.queue.pop()
        return ("Queue di hapus")
    
    #queue ukuran
    def size(self):
        return len(self.queue)
    
    #cetak seluruh elemen di queue
    def printQueue(self):
        return self.queue

list = [1,2,3,4]
myQueue = deque(list)
myQueue.append(5)
myQueue.append(6)

print(myQueue.popleft())
print(myQueue.popleft())

print myQueue