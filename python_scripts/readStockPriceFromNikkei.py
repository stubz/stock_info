# -*- coding: utf-8 -*-
import re, datetime, urllib2
from BeautifulSoup import BeautifulSoup          # For processing HTML

def main(code):
    numRegex = re.compile('\d+(\.*|\,*)\d+')
    url = "http://company.nikkei.co.jp/kessan/shihyo.aspx?scode=%s" % (code)
    url_data = urllib2.urlopen(url).read()
    soup = BeautifulSoup(url_data)
    itemNames = []
    itemValues = []
    # price info
    
    for div1 in soup('td', {'class':'brandBoxIn'}):
        for div2 in div1('div', {'class':'innerDate'}):
            for div3 in div2('div', {'class':'lineFi clearfix'}):
                for p in div3('p', {'class':'title'}):
                    itemNames.append(p.contents[0].string)
                    # print p.contents[0].string
                    txt = p.contents[0].string
                    # txt = unicode(txt, "utf-8")
                    if (txt == unicode('時価総額','utf-8') ):
                        print "lxxxxxxlll"
                for p in div3('p', {'class':'ymuiEditLink mar0'}):
                    val = p.strong.contents[0]
                    # val = re.sub("\,","", val)
                    val = re.sub("[^0-9\.\-]","", val)
                    # print val
                    itemValues.append(val)
    
    for div in soup('div', {'class':'lineFi yjMS clearfix'}):
        for p1 in div('p', {'class':'title'}):
            # print p1.contents[0].string
            itemNames.append(p1.contents[0].string)
        for p2 in div('p', {'class':'ymuiEditLink mar0'}):
            val = p2.strong.contents[0]
            val = re.sub("[^0-9\.\-]","",val)
            # print val
            itemValues.append(val)

    for i in range(len(itemValues)):
        print "%s\t:%s" % (itemNames[i], itemValues[i])

    """
    for v in itemValues: print v
    for v in itemNames: print v
    """
if __name__=='__main__':
    import sys
    if len( sys.argv ) > 1:
        code = sys.argv[1]

    main(code)
