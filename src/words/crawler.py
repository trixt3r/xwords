import requests
import wikitextparser as wtp
rq = 'http://fr.wiktionary.org/w/index.php?title='\
    + '{}&action=raw'
r = requests.get(rq.format("tomate"))

wt = wtp.parse(r.text)
# wt.tables[1].getdata()[0:3]
# print(json.dumps({'root': wt.tables[1].getdata()[0:3]}, indent=2))