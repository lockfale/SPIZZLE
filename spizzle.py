from __future__ import print_function
import socks
import socket
import time
import pprint
# http://torvps7kzis5ujfz.onion/~user/
# http://thehiddenwiki.org/
start=['http://torvps7kzis5ujfz.onion/~user/']

maxdepth=4

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}

TORSERVER='127.0.0.1'
TORPORT=9050

TIMEOUT=(25.05, 60)

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
import gc
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
	FileTransferSpeed, FormatLabel, Percentage, \
	ProgressBar, ReverseBar, RotatingMarker, \
	SimpleProgress, Timer


#yolo
requests.packages.urllib3.disable_warnings()
#this should do nothing
socket.setdefaulttimeout(65)


def getter(url):
	try:
		page = requests.get(url,headers=headers,timeout=TIMEOUT, stream=True)
		tree = html.fromstring(page.text)
		urls = tree.xpath('//a/@href')
		urls = [urljoin(page.url, x) for x in urls]
		urls=list(set(urls))
	except Exception as inst:
		return []
	return url,urls


def feeler(url):
	host=url[0]
	url=url[1]
	try:
		header=requests.head(url,headers=headers,timeout=TIMEOUT, stream=True).headers['Content-Type']
	except Exception:
		return ""
	if '.onion' in urlparse(url)[1] and 'text/html' in header:
		return host,url
	else:
		return ""


def logthis(pls):
	with open("log.txt","w") as fout:
			pprint.pprint(pls, fout)
			fout.close()
	return 1

if __name__ == '__main__':

	depth=0
	dontvisit=start

	masterall=[]
	for startlink in start:
		masterall.append(("STARTERLINK",startlink))

	masterscrape=start


	while depth<maxdepth:
		print()
		print ("depth: "+str(depth))
		print ("this depth has: "+str(len(masterscrape)))

		pool2 = multiprocessing.Pool(processes=75)
		result= pool2.map_async(getter,masterscrape,chunksize=1)
		print("Getting all the links:")
		pbar = ProgressBar(maxval=len(masterscrape),term_width=100).start()
		while not result.ready():
			pbar.update(len(masterscrape)-result._number_left)
			time.sleep(1)
		pbar.finish()

		full_masterscrape = filter(None,result.get())

		pool2.close()
		pool2.join()

		got=[]
		gc.disable()


		print("Validating and deduping links")
		pbar = ProgressBar(widgets=[Percentage(), Bar(), ETA()],maxval=100,term_width=100).start()
		#this loop is slow and needs to be faster. wtf.
		for idx,n in enumerate(full_masterscrape):
			linkhost=n[0]

			appendable=[[linkhost,actual_link] for actual_link in n[1] if actual_link not in dontvisit]
			masterappend=[(linkhost,actual_link) for actual_link in n[1]]
			dontvisitappend=[actual_link for actual_link in n[1] if actual_link not in dontvisit]

			got+=appendable
			masterall+=masterappend
			dontvisit+=dontvisitappend

			pbar.update(100 * idx/len(full_masterscrape))
		gc.enable()
		pbar.finish()

		pool = multiprocessing.Pool(processes=150)
		result=pool.map_async(feeler,got,chunksize=1)

		print("Finding all the HTML/TEXT pages")

		if len(got) == 0:
			print("detecting large amounts of fail")
			continue

		pbar = ProgressBar(maxval=len(got),term_width=100).start()
		while not result.ready():
			pbar.update(len(got)-result._number_left)
			time.sleep(1)
		pbar.finish()

		real_result = filter(None,result.get())

		pool.close()
		pool.join()

		for restuple in real_result:
			masterall.append(restuple)

		masterscrape=[]
		for lank_tuple in real_result:
			masterscrape.append(lank_tuple[1])

		masterscrape=list(set(masterscrape))
		masterall=list(set(masterall))
		dontvisit=list(set(dontvisit))
		depth+=1
		print ("**********")
		print ("depth complete")

	print ("+++++++++++")
	print ("all done! total: "+str(len(masterall)))
	#logging needs to be done better
	logthis(masterall)