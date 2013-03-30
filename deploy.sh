#!/bin/bash
cd /opt/cad/
python cadrss.py
mv rss.xml /usr/share/nginx/www/cad.xml
