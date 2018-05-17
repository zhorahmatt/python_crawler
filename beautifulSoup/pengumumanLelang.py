import urllib2
from bs4 import BeautifulSoup


def make_soup(url):
    pages = urllib2.urlopen(url)
    soupData =  BeautifulSoup(pages, "html.parser")
    return soupData

