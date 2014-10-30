#!/usr/local/bin/python
import sys

sys.path.append('./lib/')
import stock_db
#
# establish connection
con = stock_db.connect()
cur = con.cursor()
#
# # get list of stock code
sql = "SELECT DISTINCT stockCode FROM stockName"
cur.execute(sql)
stockCodeList = cur.fetchall()
#

for code in stockCodeList:
    print code[0]

cur.close()
con.close()
