import urllib2
import json

class Idlelang():
    
    id_lelang = []
    content = urllib2.urlopen("http://lpse.pangkepkab.go.id/eproc4/dt/lelang").read()
    result = json.loads(content)

    links = []
    for ids in result["data"]:
        link = "https://lpse.makassar.go.id/eproc4/lelang/"+ids[0]+"/pengumumanlelang"
        links.append(link)
    print links
    