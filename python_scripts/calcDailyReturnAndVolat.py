#!/bin/env python

import sys
import datetime
# sys.path.append('./lib/')
sys.path.append('/Users/popopopo/myWork/python/lib')
import stock_db
from dateutil import relativedelta
from numpy import *

def insertReturnAndVolatEstimateToTable(con, stockcd, mktcd, date, ret, logret, ret3mon, volat3mon,
            ret6mon, volat6mon, ret1year, volat1year, ret3year, volat3year, ret5year, volat5year):
    """
    insert estimated return and volatility into a table
    """
    sql = """
            insert into %s (date, stockcd, marketcd, ret, logret, ret3mon, volat3mon,
                        ret6mon, volat6mon, ret1year, volat1year, ret3year, volat3year, ret5year, volat5year)
            values ('%s','%s','%s',%s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s);
        """
    sql = sql % (stock_db.tblPerfDaily, date, stockcd, mktcd, ret, logret, ret3mon, volat3mon,
            ret6mon, volat6mon, ret1year, volat1year, ret3year, volat3year, ret5year, volat5year)
    # print sql

    try:
        con.query(sql)
    except:
        print "sql failed : %s" % (sql)

def calcDailyReturnAndVolatForStockData(stockData):
    con = stock_db.connect()

    cdlist = stock_db.getStockCodeListCurrent()

    # calculate daily return ( log return as well ) for each stock
    for stockcd, mktcd in stockData.keys():
        # do not compute anything if stock is no longer listed
        if not ( stockcd, mktcd ) in cdlist:
            continue
        datelist = stockData[(stockcd, mktcd)]['date']
        stockval = array(stockData[(stockcd, mktcd)]['close'])
        # get daily return and daily log return
        ret = stock_db.getStockReturnArray(stockval)
        logret = stock_db.getStockLogReturnArray(stockval)
        
        # calculate historical estimates of annual return and volatility
        for i in range(len(ret)):
            # we need at least data for 3-month long
            # 期待リターン、ボラティリティを既に計算している日付分については計算しない。
            # stockPerfDailyの最新日付以降についてのみ計算を行う。データは日付の新しい順に入っている前提
            if len(ret[i:]) < stock_db.DAY_MONTH*3 or datelist[i] <= latestdate:
                break

            # get 3-month, 6-month, 1-year, 3-year, 5-year return and volatility estimate
            retvol_matrix = stock_db.getReturnAndVolatEstimateByPeriod(ret[i:], data_length=[
                stock_db.DAY_MONTH*3, stock_db.DAY_MONTH*6, stock_db.DAY_YEAR, stock_db.DAY_YEAR*3, stock_db.DAY_YEAR*5])

            # insert these estimated returns and volatilities into a table
            insertReturnAndVolatEstimateToTable(con, stockcd, mktcd, datelist[i], ret[i], logret[i],
                retvol_matrix[0][0], retvol_matrix[0][1],
                retvol_matrix[1][0], retvol_matrix[1][1],
                retvol_matrix[2][0], retvol_matrix[2][1],
                retvol_matrix[3][0], retvol_matrix[3][1],
                retvol_matrix[4][0], retvol_matrix[4][1])

        con.commit()
        print "inserted %s data..." % (stockcd)

    con.close()

####################################################################################################
####################################################################################################
####################################################################################################

if __name__=='__main__':
    """
    compute all estimated return and volatilities until today
    """

    print("\n\n%s\n\n" % ("*"*80))
    print("******* calculate estimated returns and volatilities from %s *******\n\n" % (stock_db.tblPriceDaily))

    con = stock_db.connect()

    # delete all rows in stockPerfDaily
    # sql = "truncate table stockPerfDaily;"
    # cur.execute(sql)

    print " getting latest date of the stockPerfDaily ",
    # latestdate = stock_db.getLatestDateInStockPriceHist()
    # １回目は（テーブルに何もない状態のとき）日付を直接指定する
    # latestdate = datetime.date(2000, 1, 4)
    latestdate = stock_db.getLastDateFromTable(stock_db.tblPerfDaily)
    # 日時データが存在する最新の日付を取得する
    enddate   = stock_db.getLastDateFromTable(stock_db.tblPriceDaily)
    # 最新の日付を取得する
    startdate = latestdate-datetime.timedelta(365*5+1)

    print " : ", latestdate
    print ""
    # cdlist = stock_db.getStockCodeListCurrent()

    # 市場コードのリストを取得する
    mktcdlist = stock_db.getStockMarketCode()

    for mktcd in mktcdlist:
        print "extracting data from %s between %s and %s" % (stock_db.tblPriceDaily, startdate, latestdate)
        stockData = stock_db.getStockHistDailyByDate2(start=startdate, end=enddate, mktcd=mktcd, tblStockPriceHist=stock_db.tblPriceDaily, columns=['close'])
        print "\n----- start computing return and volatility for market code = '%s'-----\n" % ( mktcd )
        calcDailyReturnAndVolatForStockData(stockData)

