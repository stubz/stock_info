import os, sys
from datetime import datetime
from subprocess import call
sys.path.insert(0, "/Users/tatata/myWork/python")
import MySQLdb
import stock_db

filename = "MNAME"
filenameLZH = filename+".LZH"
filenameCSV = filename+".CSV"
testPath = '/Users/popopopo/myWork/stock_info/perl_scripts/'
fileFullPath = testPath+filenameCSV

def execute(cmd):
    status = True
    try:
        ret = call(cmd, shell = True)
        if ret < 0:
            print >> sys.stderr, "The child process was exited by signal.", -ret
            status = False

    except OSError, e:
        print >> sys.stderr, "failed to execute.:", e
        status = False

    return status


def downloadStockNameFile(nameFileLZH, path_to_dat):
    """
    download MNAME.LZH file to a specified directory
    """
    yyyy = datetime.today()
    # -q : turn off wget's output
    # -P : set directro prefix
    # -N : turn on time-stamping
    # -nH: no host name
    cmd = "wget --tries=5 -N -nH -q -P %s http://www.edatalab.net/kabu/data%s/%s" % (
        path_to_dat,
        yyyy.strftime('%Y'),
        nameFileLZH
            )
    # download lha file if there is an update.
    # call(cmd, shell=True)
    if not execute(cmd):
        return False

    lhacmd = "lha egq %s" % nameFileLZH
    if not execute(lhacmd):
        return False

# create table stockNameYYYYMMDD
def createStockNameTable(date):
    tableName = "stockName%s" % date
    sql = "CREATE TABLE %s" % tableName
    print sql
    con = stock_db.connect()
    try:
        cur = con.cursor()
        # cur.execute(sql)
    except MySQLdb.IntegrityError, ie:
        print "%s : %s" % (tableName, ie)
    except MySQLdb.Error, e:
        print "%s : %s" % (tableName, e)

# insert MNAME.CSV to stockName
def updateStockNameTable(fileName):
    tableName = "stockName"
    # sql = "TRUNCATE TABLE %s" % tableName

    file_object = open(fileName)
    try:
        for line in file_object:
            # remove new line 
            str = line.rstrip('\r\n')
            # remove double quotation
            str = str.replace('\"','')
            stockCode, stockName = str.split(',')[:2]

            # create sql 
            sql = "INSERT INTO %s (stockCode, stockName) VALUES (%s, %s)" % (tableName, stockCode, stockName)
            print sql

    finally:
        file_object.close()

# rename MNAME.CSV with valid date
def renameFileName(name, date):
    pass


# 
#

if __name__ == '__main__':

    sys.path.append(testPath)

# downloadStockNameFile(filenameLZH, testPath)

    createStockNameTable(20081119)

    print filenameCSV
    updateStockNameTable(filenameCSV)
    # updateStockNameTable(fileFullPath)

    # connect to stock_db
    con = stock_db.connect()
    try:
        cur = con.cursor()
    except MySQLdb.Error, e:
        print "query failed"
        print e

    cur.close()
    con.close()


