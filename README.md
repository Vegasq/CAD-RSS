CAD-RSS
=======

Ctrl+Alt+Del comics RSS generator.

===Test:===
http://cad.lifeandsticker.com/


===Usage:===

#!/bin/bash
# Open folder with script
cd /opt/cad/
# Execute
python cadrss.py
# Move to web server
mv rss.xml /usr/share/nginx/www/cad.xml

===Cron:===

I use each 5 hours update
0 */5 * * * /opt/cad/deploy.sh
