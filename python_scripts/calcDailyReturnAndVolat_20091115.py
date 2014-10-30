#!/bin/env python

import sys
import datetime
# sys.path.append('./lib/')
sys.path.append('/Users/popopopo/myWork/python/lib')
import stock_db
from dateutil import relativedelta
from numpy import *

# $B4|4V$N$?$a$NDj?t(B
DAY_MONTH = 21
DAY_YEAR  = 245

def getReturnAndVolatEstimate(ret_arr):
    if ret_arr == None or len(ret_arr) < 2:
        return ( "\\N" , "\\N" ) # null value for MySQL
    else:
        daycnt = len(ret_arr)
        # $BG/N(49;;$7$FJV$9(B
        return ( ret_arr.mean()*DAY_YEAR, ret_arr.std()*sqrt(DAY_YEAR) )

def getStockValueArray(val_arr, datelist, start, end):
    try:
        idxstart = datelist.index(start)
        idxend   = datelist.index(end)
        print "idxstart:%d  idxend:%d   %s %s" % (idxstart, idxend, start, end)
        return val_arr[idxstart:idxend+1]
    except ValueError, e:
        # $B0lCW$9$kF|IU$,8+$D$+$i$J$$>l9g$O!";XDj$7$?F|IU$rD6$($k:G=i$NF|IU$^$G$r<hF@(B
        idxstart = len([x for x in datelist if x > start])
        return val_arr[idxstart:idxend+1]
    except:
        return None

def getStockReturnArray(val_arr):
    """
    return a list of return
    """
    try:
        return val_arr[0:-1]/val_arr[1:]-1
    except TypeError, e:
        return [0]
    except:
        pass

def getStockLogReturnArray(val_arr):
    """
    return a list of log return
    """
    try:
        return log(val_arr[0:-1]/val_arr[1:])
    except TypeError, e:
        return [0]
    except:
        pass

def insertReturnAndVolatEstimateToTable(stockcd, mktcd, date, ret, logret, ret3mon, volat3mon,
            ret6mon, volat6mon, ret1year, volat1year, ret3year, volat3year, ret5year, volat5year):
    """
    insert estimated return and volatility into a table
    """
    con = stock_db.connect()
    cur = con.cursor()
    sql = """
            insert into stockPerfDaily (date, stockCode, marketCode, ret, logret, ret3mon, volat3mon,
                        ret6mon, volat6mon, ret1year, volat1year, ret3year, volat3year, ret5year, volat5year)
            values ('%s','%s','%s',%s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s);
        """
    sql = sql % (date, stockcd, mktcd, ret, logret, ret3mon, volat3mon,
            ret6mon, volat6mon, ret1year, volat1year, ret3year, volat3year, ret5year, volat5year)

    # cur.execute(sql)
    print sql

    cur.close()
    con.close()


if __name__=='__main__':
    con = stock_db.connect()
    cur = con.cursor()

    print " getting latest date of the stock data....",
    latestdate = stock_db.getLatestDateInStockPriceHist(cur)
    print " : ", latestdate
    print " getting a list of date...."
    cdlist = stock_db.getStockCodeList(latestdate)

    # $B#3%v7n!"#6%v7n!"#1G/!"#3G/!"#5G/$N4|4V$r7W;;$9$k(B
    # $BJX59E*$K!"#1%v7n(B21$BF|!"#1G/(B245$BF|$G7W;;$9$k(B
    date5year = latestdate + relativedelta.relativedelta(years=-5)

    # datelist = stock_db.getDailyDateList(cur, date5year, latestdate)
    
    # get historical data for all stocks at one time.
    # and save that into hash
    # stockData = stock_db.getStockHistDailyByDate(start=date5year, end=latestdate)
    stockData = stock_db.getStockHistDailyByDate2(start=date5year, end=latestdate, mktcd='1', columns=['close'])

    # loop for each (stockCode, marketCode) pair

    for stockcd, mktcd in stockData.keys():
        if not (stockcd, mktcd) in cdlist:
            continue
        datelist = stockData[(stockcd, mktcd)]['date']
        stockval = stockData[(stockcd, mktcd)]['close']
        # $B;XDj$7$?4|4V$N3t2A%G!<%?$r@Z$j=P$7(B
        if len(datelist) < DAY_YEAR*5:
            val5year = None
        else:
            val5year = array(stockval[0:DAY_YEAR*5+1])
        if len(datelist) < DAY_YEAR*3:
            val3year = None
        else:
            val3year = array(stockval[0:DAY_YEAR*3+1])
        if len(datelist) < DAY_YEAR:
            val1year = None
        else:
            val1year = array(stockval[0:DAY_YEAR+1])
        if len(datelist) < DAY_MONTH*6:
            val6mon = None
        else:
            val6mon = array(stockval[0:DAY_MONTH*6+1])
        if len(datelist) < DAY_MONTH*3:
            val3mon = None
        else:
            val3mon = array(stockval[0:DAY_MONTH*3+1])

        # $B%j%?!<%s$H%\%i%F%#%j%F%#$r7W;;(B
        if val5year == None:
            ret5year, vol5year = "\\N", "\\N"
        else:
            ret5year, vol5year = getReturnAndVolatEstimate( getStockReturnArray(val5year) )
        if val3year == None:
            ret3year, vol3year = "\\N", "\\N"
        else:
            ret3year, vol3year = getReturnAndVolatEstimate( getStockReturnArray(val3year) )
        if val1year == None:
            ret1year, vol1year = "\\N", "\\N"
        else:
            ret1year, vol1year = getReturnAndVolatEstimate( getStockReturnArray(val1year) )
        if val6mon == None:
            ret6mon, vol6mon = "\\N", "\\N"
        else:
            ret6mon, vol6mon = getReturnAndVolatEstimate( getStockReturnArray(val6mon) )
        if val3mon == None:
            ret3mon, vol3mon = "\\N", "\\N"
        else:
            ret3mon, vol3mon = getReturnAndVolatEstimate( getStockReturnArray(val3mon) )

        print "stockCD : %s   marketCode : %s" % (stockcd, mktcd)
        # $B%G!<%?%Y!<%9$K%G!<%?$rF~$l$k(B
        insertReturnAndVolatEstimateToTable(stockcd, mktcd, latestdate, 
                getStockReturnArray(val3mon)[0], getStockLogReturnArray(val3mon)[0],
                ret3mon, vol3mon, ret6mon, vol6mon, ret1year, vol1year, 
                ret3year, vol3year, ret5year, vol5year)

