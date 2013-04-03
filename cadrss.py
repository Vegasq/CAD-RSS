#!/usr/bin/python3

try:
    import requests
    from bs4 import BeautifulSoup
    from jinja2 import Template
except ImportError:
    raise Exception('Please run "sudo apt-get install python-requests python3-requests python-beautifulsoup python-jinja2 python3-jinja2"')

import re
import datetime

class CADRss:
    count = 10
    basic_url = "http://www.cad-comic.com"
    start_from = "/cad/"
    result = []
    d = re.compile(r".*(\d{4}-\d{2}-\d{2}).*")
    updated = False

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

    def read(self, url=False):
        if url == False:
            url = self.start_from
        open_url = "%s%s" % (self.basic_url, url)

        data = requests.get(open_url)
        soup = BeautifulSoup(data.text)
        title = soup.find('title').text

        d = self.d.split(title)
        year, mon, day = d[1].split('-')
        pubDate = datetime.datetime(int(year), int(mon), int(day), 10, 10, 10)
        pubDate = pubDate.strftime("%a, %d %b %Y %H:%M:%S %z")
        if not self.updated:
            self.updated = pubDate

        cont = soup.find(id='content')
        back = soup.find_all("a", text="Back")
        i = cont.find('img')
        html = i.encode('ascii').decode('utf-8')
        next_url = back[0].attrs['href']
        self.result.append((title, open_url, html, pubDate))



        self.count -= 1
        if not self.count:
            return True
        return self.read(next_url)

    def render(self, fl):
        template = Template(self.template)
        fl.write(template.render(items=self.result, link=self.basic_url, updated=self.updated))
        return fl


ri = CADRss()
ri.read()

f = open('rss.xml', 'w')
f = ri.render(f)
f.close()
