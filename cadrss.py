#!/usr/bin/python3

try:
    import requests
    from bs4 import BeautifulSoup
    from jinja2 import Template
except ImportError:
    raise Exception('Please run "sudo apt-get install python-requests python3-requests python-beautifulsoup python-jinja2 python3-jinja2"')


class CADRss:
    count = 10
    basic_url = "http://www.cad-comic.com"
    start_from = "/cad/"
    result = []

    template = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <author>Ctrl+Alt+Del</author>
    <title>Ctrl+Alt+Del</title>
    {% for item in items %}
    <entry>
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
        cont = soup.find(id='content')
        back = soup.find_all("a", text="Back")
        i = cont.find('img')
        html = i.encode('ascii').decode('utf-8')
        next_url = back[0].attrs['href']
        self.result.append((title, open_url, html))

        self.count -= 1
        if not self.count:
            return True
        return self.read(next_url)

    def render(self, fl):
        template = Template(self.template)
        fl.write(template.render(items=self.result, link=self.basic_url))
        return fl


ri = CADRss()
ri.read()

f = open('rss.xml', 'w')
f = ri.render(f)
f.close()
