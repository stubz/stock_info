#/usr/bin/env python
import MySQLdb
con = MySQLdb.connect(
        host='192.168.1.100',
        port=3306,
        user='stock',
        passwd='stock',
        db='stock_db')

