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

class CADRss:
    count = 10
    basic_url = "http://www.cad-comic.com"
    native_rss = "http://www.cad-comic.com/rss/rss.xml"
    start_from = "/cad/"
    result = []
    d = re.compile(r".*(\d{4}-\d{2}-\d{2}).*")
    d2 = re.compile(r"Ctrl\+Alt\+Del - (?P<title>.*) \((?P<date>\d{4}-\d{2}-\d{2})\)")
    updated = False

    atom = '<atom:link href="http://www.cad-comic.com/rss/" rel="self" type="application/rss+xml" />'

    template = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <author>
        <name>Ctrl+Alt+Del</name>
        <email>pierre@cad-comic.com</email>
    </author>
    <title>Ctrl+Alt+Del</title>
    <link>http://www.cad-comic.com/</link>
    <updated>{{ updated }}</updated>
    <description>RSS for the popular comic Ctrl+Alt+Del</description>
    <webMaster>pierre@cad-comic.com (Pierre-Luc Brunet)</webMaster>
    <copyright>Copyright 2002-2013 Tim Buckley and Ctrl+Alt+Del Productions. All rights reserved.</copyright>
    <language>en-us</language>

    {% for item in items %}
    <entry>
        <updated>{{ item[3] }}</updated>
        <pubDate>{{ item[3] }}</pubDate>
        <title>{{ item[0] }}</title>
        <link href="{{ item[1] }}"/>
        <content type="html"><![CDATA[{{ item[2] }}]]></content>
    </entry>
    {% endfor %}
</feed>"""

    def get_soup(self, request_obj):
        soup = False

        try:
            txt = request_obj.text
        except AttributeError:
            txt = request_obj.content
        txt = txt.replace(self.atom, '')
        soup = BeautifulSoup(txt, "xml")

        return soup

    def __init__(self):
        self.native_soup = self.read_original_atom()
        self.read()
        self.merge()
        
    def merge(self):
        for item in self.native_soup.find_all('item'):
            for page in self.result:
                ttl = str(item.find('title'))[21:-8]
                if page[0] == ttl:
                    desc = item.find('description')
                    item.find('description').string = "%s" % page[2]
                    # item.find('description').decode_contents()


    def read_original_atom(self):
        native_data = requests.get(self.native_rss)
        # Python2/3 comp
        native_soup = self.get_soup(native_data)

        items = native_soup.find_all('item')

        for i in items:
            # i = self.get_soup(i)
            if i.find('category').text == 'Ctrl+Alt+Del':
                pass
            else:
                i.extract()
        return native_soup

    def read(self, url=False):
        # Set url for first iter
        if url == False:
            url = self.start_from
        open_url = "%s%s" % (self.basic_url, url)

        # Send request
        data = requests.get(open_url)
        try:
            soup = BeautifulSoup(data.text, "xml")
        except AttributeError:
            soup = BeautifulSoup(data.content, "xml")

        
        # Save page title...
        title = soup.find('title').text
        d = self.d2.split(title)

        # ... and extract
        year, mon, day = d[2].split('-')
        pubDate = datetime.datetime(int(year), int(mon), int(day), 10, 10, 10)
        pubDate = pubDate.strftime("%a, %d %b %Y %H:%M:%S %z")
        if not self.updated:
            # Save last update date
            self.updated = pubDate

        # Biggest div
        cont = soup.find(id='content')

        # URL to next comics
        back = soup.find_all("a", text="Back")
        next_url = back[0].attrs['href']

        # Image
        i = cont.find('img')
        html = i.encode('ascii').decode('utf-8')

        self.result.append((d[1], open_url, html, pubDate))

        self.count -= 1
        if not self.count:
            return True
        return self.read(next_url)

    def render(self, fl):
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
