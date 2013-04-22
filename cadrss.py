#!/usr/bin/python3
# Nikolay Yakovlev <niko.yakovlev@yandex.ru>
# 2013


try:
    import requests
    from bs4 import BeautifulSoup
    from jinja2 import Template
except ImportError:
    raise Exception('Please run "sudo apt-get install python-requests python3-requests python-beautifulsoup python-jinja2 python3-jinja2 python3-bs4 python-bs4"')

import re
import datetime
import sqlite3

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'



class CADB:
    ''' SQLite abstraction '''
    #Define
    conn = False

    def db_save(self, title, descr):
        ''' Save if doesn't exists '''
        print(self.OKBLUE + "[DB_SAVE]" + self.ENDC + " '%s' " % title )
        res = self.db_cursor().execute('SELECT * FROM cad WHERE `title` = "%s" ' % (title))
        if res.fetchone() == None:
            self.db_cursor().execute('INSERT INTO cad(title,descr) VALUES(?,?)', (title,descr,))
            self.conn.commit()

    def db_get(self, title):
        ''' Return result, could be None '''
        print(self.OKBLUE + "[DB_GET]" + self.ENDC + " '%s' " % title )
        res = self.db_cursor().execute('SELECT * FROM cad WHERE `title` = "%s" ' % (title))
        return res.fetchone()

    def db_cursor(self):
        ''' Return coursor '''
        if self.conn == False:
            print(self.OKBLUE + "[DB_CURSOR]" + self.ENDC + " Creating..." )
            self.conn = sqlite3.connect('cad.db')
            self.cur = self.conn.cursor()
            self.cur.execute("CREATE TABLE IF NOT EXISTS cad \
                (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,title TEXT, descr TEXT)")
        return self.cur



class NativeDataParser:
    count = 10
    basic_url = "http://www.cad-comic.com"
    native_rss = "http://www.cad-comic.com/rss/rss.xml"
    start_from = "/cad/"
    # d = re.compile(r".*(\d{4}-\d{2}-\d{2}).*")
    d2 = re.compile(r"Ctrl\+Alt\+Del - (?P<title>.*) \((?P<date>\d{4}-\d{2}-\d{2})\)")
    atom = '<atom:link href="http://www.cad-comic.com/rss/" rel="self" type="application/rss+xml" />'

    def get_soup(self, request_obj):
        soup = False

        try:
            txt = request_obj.text
        except AttributeError:
            txt = request_obj.content
        txt = txt.replace(self.atom, '')
        soup = BeautifulSoup(txt, "xml")

        return soup

    def read_original_feed(self):
        print(self.OKGREEN + "[NDP_READ_FEED]" + self.ENDC + " Retrieve %s" % self.native_rss )

        native_data = requests.get(self.native_rss)
        # Python2/3 comp
        native_soup = self.get_soup(native_data)
        items = native_soup.find_all('item')

        for i in items:
            if i.find('category').text != 'Ctrl+Alt+Del':
                i.extract()
        return native_soup

    def read_original_site(self, url=False):
        # Set url for first iter
        if url == False:
            url = self.start_from
        print(self.OKGREEN + "[NDP_READ_SITE]" + self.ENDC + " Retrieve %s" % url )

        # Send request
        soup = self.get_soup(requests.get("%s%s" % (self.basic_url, url)))
        
        # Save page title...
        d = self.d2.split(soup.find('title').text)

        # URL to next comics
        back = soup.find_all("a", text="Back")
        next_url = back[0].attrs['href']

        # Image
        i = soup.find(id='content').find('img')
        html = i.encode('ascii').decode('utf-8')

        # Save to DB
        self.db_save(d[1], html)

        self.count -= 1
        if not self.count:
            return True
        return self.read_original_site(next_url)



class CADRss(CADB, NativeDataParser, Colors):
    def __init__(self):
        self.native_soup = self.read_original_feed()
        # self.read_original_site()
        self.merge()


    def merge(self):
        print(self.WARNING + "[CAD_RSS]" + self.ENDC + " Comparing DB with feed..." )
        for item in self.native_soup.find_all('item'):
            ttl = str(item.find('title'))[21:-8]
            row = self.db_get(ttl)
            if row != None:
                item.find('description').string = "%s" % row[2]
            else:
                self.read_original_site()
                row = self.db_get(ttl)
                item.find('description').string = "%s" % row[2]

    def render(self, fl):
        print(self.WARNING + "[CAD_RSS]" + self.ENDC + " Saving result..." )

        txt = self.native_soup.prettify().replace('<channel>', '<channel>\n%s' % self.atom)
        txt = txt.replace("<description>", "<description>\n<![CDATA[ ")
        txt = txt.replace("</description>", "]]>\n</description>")
        txt = txt.replace("&lt;", "<")
        txt = txt.replace("&gt;", ">")
        fl.write(txt)
        return fl


ri = CADRss()

f = open('rss.xml', 'w')
f = ri.render(f)
f.close()
