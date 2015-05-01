import socks
import socket
import time

start=['http://torvps7kzis5ujfz.onion/~user/']

maxdepth=2

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}

TORSERVER='127.0.0.1'
TORPORT=9050

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,TORSERVER, TORPORT)
socket.socket = socks.socksocket

def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
socket.getaddrinfo = getaddrinfo


from urlparse import urljoin
from urlparse import urlparse
import multiprocessing
from lxml import html
import requests


def getter(url):
	try:
		page = requests.get(url,headers=headers)
		tree = html.fromstring(page.text)
		urls = tree.xpath('//a/@href')
		urls = [urljoin(page.url, url) for url in urls]
		newset=set(urls)
		urls=list(newset)
	except Exception:
		return []

	print "got: "+str(len(urls))+" urls"
	return urls

def feeler(url):
	try:
		header=requests.head(url,headers=headers).headers['Content-Type']
	except Exception:
		return ""
	if '.onion' in urlparse(url)[1] and 'text/html' in header:
		return url
	else:
		print "bad"
		print header
		return ""

def spider(tovisit):
	print "visiting: "+tovisit
	got=getter(tovisit)

	pool = multiprocessing.Pool(processes=100)
	result=pool.map_async(feeler,got,chunksize=1)

	while not result.ready():
		print("num left: {}".format(result._number_left))
		time.sleep(10)
	real_result = result.get()

	pool.close()

	pool.join()

	return got,filter(None,real_result)


if __name__ == '__main__':

	depth=0
	masterall=[]
	masterscrape=start
	dataout={}

	while depth<maxdepth:
		premaster=[]
		for idx,item in enumerate(masterscrape):
			print "depth: "+str(depth)+" Index: "+str(idx)+" of: "+str(len(masterscrape))
			goodlinks, allinks=spider(item)
			dataout[item]=[depth,goodlinks,allinks]
			premaster+=goodlinks
			masterall+=allinks
		print len(premaster)
		print len(masterall)
		masterscrape=[aa for aa in list(set(premaster)) if aa not in masterall]
		masterall=list(set(masterall))
		depth+=1