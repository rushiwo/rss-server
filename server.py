import requests
from flask import Flask
from flask import Response
import datetime
from rfeed import *
from bs4 import BeautifulSoup
import time
import json
import re
from threading import Thread,Lock
logname = ""
password = ""
payload = {'username':logname,'password':password}
        # print(r.text)
s = requests.Session()
# start=time.time_ns()
url='https://www.tjupt.org/torrents.php?incldead=0&spstate=2&picktype=0&inclbookmarked=0&search=&search_area=0&search_mode=0'
all_torrents=[]
rss_doc=''
r = s.post("https://www.tjupt.org/takelogin.php",data=payload,timeout=10)
items=[]
lock = Lock()
def genrss():

    global url, all_torrents, rss_doc, s, lock
    while True:
        html_doc = s.get(url,timeout=10)
        soup = BeautifulSoup(html_doc.text,'lxml')
        torrents = soup.find_all("table","torrents")[0]


        for item in torrents.tr.find_next_siblings('tr'):
            all_links = item.table.tr.find_all("a")
            title = all_links[0]['title']
            enclosure = 'https://www.tjupt.org/'+all_links[1]['href']+'&passkey='
            link = 'https://www.tjupt.org/'+all_links[0]['href']
            size=0
            seeders=0
            peers=0
            total_downloader=0

            tds = item.td.find_next_siblings('td')
            td=tds[3]
            if td.contents[2]=='MiB':
                size = int(float(td.contents[0])*1024*1024)
            elif td.contents[2]=='GiB':
                size = int(float(td.contents[0])*1024*1024*1024)
            else :
                size = 0

            td=tds[4]

            if td.string=='0':
                seeders = 0
            else:
                seeders = int(td.a.string.replace(',',''))
            td=tds[5]
            if td.string=='0':
                peers = 0
            else:
                peers = int(td.a.string.replace(',',''))
            td=tds[6]

            if td.string=='0':
                total_downloader = 0
            else:
                total_downloader = int(td.a.b.string.replace(',',''))
            all_torrents.append({
                'title':title,
                'enclosure':enclosure,
                'link':link,
                'seeders':seeders,
                'peers':peers,
                'total_downloader':total_downloader,
                'size':size
            })
            k=1
        for t in all_torrents:
            des=s.get(t['link'])
            print(k)
            k=k+1
            #soup = BeautifulSoup(des.text,'lxml')
            has = re.search(r"◎简(.|\n)*<font",des.text,re.M)
            #print(has)
            if has:
                description = has.group()[0:-5]
            else:
                description = '无简介'
            items.append(Item(title = t['title'],
                              link = t['link'],
                              description = description.replace("<br />","\n").replace("&nbsp;","").strip(),
                              enclosure = Enclosure(url =t['enclosure'] , length = t['size'], type = 'application/x-bittorrent')
                              ))

        feed = Feed(title = "北洋园PT Free Torrents",
                     link = "https://www.tjupt.org",
                     description = "Latest free torrents from 北洋园PT",
                     language = "zh-cn",
                     lastBuildDate = datetime.datetime.now(),
                     items = items)
        lock.acquire()
        rss_doc = feed.rss()
        lock.release()
        time.sleep(120)

        # print(html_doc.text)
        # stop = time.time_ns()
        # print("time:"+str((stop-start)/(10**9)))

        # lock = Lock()

        # def hello():

        #     while True:


        #         lock.acquire()

        #         lock.release()
        #         time.sleep(1)

        # t1 = Thread(target=hello,daemon=True)
        # t1.start()
        # print(r.text)

t1 = Thread(target=genrss,daemon=True)
t1.start()
app = Flask(__name__)

@app.route("/rss")
def rss():
    resp = Response(rss_doc)
    resp.headers['content-type'] = 'text/xml; charset=UTF-8'
    return resp
if __name__ == "__main__":
    app.run(host='0.0.0.0')

