import urllib2
import json
import pymongo
from pymongo import MongoClient
import pprint
from collections import deque
import time

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
    for mongo_url in mongo_lpse_url_list.find({"status_url" : 0}):
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
            insert_data = True
            if insert_data:
                success_data = eDatabase.eproc_url_lists
                success_data.update_many(
                    {"_id" : ids[id]},
                    {"$set" : {
                        "status_url" : 1.0
                    }
                    }
                )
                lists = True
            else:
                lists = False
        except urllib2.URLError as e:
            print "errorki ndi ku di URL Error"
            #save ke database errornya
            error_data = eDatabase.eproc_url_lists
            error_data.update_many(
                {"_id" : ids[id]},
                {"$set" : {
                    "status_url" : 0.0
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

def testing_using_database():
    database = db_connection()
    urls = database.eproc_url_lists
    name = []
    for url in urls.find({"status_url" : 0}):
        url.update_one(
            {"url" : url["url"]},
            {"$set" : {
                "status_url" : 1
                }
            }
        )
    return name

def testing():
    urls, ids = get_url_list()
    database = db_connection()
    url_mongo_list = database.eproc_url_lists
    
    status = []
    for id in ids:
        stat = url_mongo_list.find_one({"_id" : id})
        status.append(stat)
    return status
#main
anjay = httpReq()
print anjay
