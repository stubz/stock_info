# -*- coding:utf-8 -*-
# $BCM$,$D$+$J$$>l9g3t2A$,(BO$B$GEPO?$5$l$k!#$=$N$?$a$K%\%i%F%#%j%F%#!<7W;;$J$I$G;HMQ$G$-$J$$!#(B
# $B%<%m$N>l9g$OD>6a$N%<%mD6$NF|IU$N3t2A$G@v$$BX$($k(B
#
import stock_db

# $B%F!<%V%kL>(B
tblPriceDailyRaw   = 'priceDailyRaw'
tblPriceDaily      = 'priceDaily'
tblPriceWeeklyRaw  = 'priceWeeklyRaw'
tblPriceWeekly     = 'priceWeekly'
tblPriceMonthlyRaw = 'priceMonthlyRaw'
tblPriceMonthly    = 'priceMonthly'

def getZeroValueStockList(tbl, date):
    """
    $B3t2A$,%<%m$NLCJA$N%3!<%I!";T>l%3!<%I!"F|IU$N%?%W%k$r%j%9%H$KJ]B8$9$k(B
    """
    con = stock_db.connect()

    # $B;OCM!"9bCM!"0BCM!"=*CM!"<h0z9b$NCf$+$i$I$N9`L\$r<hF@$9$k$+;XDj$9$k!#(B
    # $B$I$N9`L\$K$b%^%C%A$7$J$$>l9g$O=*CM$@$1JV$9(B
    """
    columns = filter((lambda x: x in ['open', 'high', 'low', 'close', 'volume']), columns)
    if len(columns) == 0:
        print "None of ['open','high','low','close','volume'] are given. will return 'close' only."
        columns = ["close"]

    """

    sql = """select date, stockcd, marketcd from %s
                 where date = '%s' and (close<=0 or close is null) """ % (tbl, date)

    try:
        con.query(sql)
        r = con.use_result()
    except:
        print "failed to get data"
        con.close()
        return None

    stockdata = [] 
    while(True):
        row = r.fetch_row(1,1) # get one row as a dictionary
        if not row: break
        data = row[0] # [0] since fetch_row returns a tuple
        # $BLCJA%3!<%I$H;T>l%3!<%IF|IU$r%-!<$K$7$F%G!<%?$r(Bdictionary$B$KJ]B8$9$k(B
        stockKey  = (data['stockcd'], data['marketcd'], date)
        stockdata.append(stockKey)

    con.close()
    return stockdata

def getLatestNonZeroPrice(stockcd, marketcd, date):
    """
    $BD>6a$NF|IU$+$i0lHV6a$$F|IU$G!"3t2A$,#0$G$O$J$$F|IU$N=*CM$r<hF@$9$k(B
    """
    con = stock_db.connect()
    sql = """select close from stockPriceHistDaily where stockcd='%s' and marketcd='%s' and 
                date < '%s' and close > 0 order by date limit 1
            """ % (stockcd, marketcd, date)
    try:
        con.query(sql)
        r = con.use_result()
    except:
        print "failed to get data"
        con.close
        return None

    row = r.fetch_row(1,1)
    stockprice = row[0]['close']
    con.close()
    return stockprice

def updateZeroPriceStock(stockcd, marketcd, date, price):
    """
    $B3t2A$,#0$@$C$?LCJA$N=*CM$@$1=$@5$9$k(B
    """
    con = stock_db.connect()
    sql = """update stockPriceHistDaily set close = %s
            where stockcd = '%s' and marketcd = '%s' and date='%s'""" % ( price, stockcd, marketcd, date )
    print sql
    try:
        # con.query(sql)
        con.close()
    except:
        # print "sql failed : %s" % (sql)
        con.close()
    


################################################################################

if __name__=='__main__':
    import sys
    # sys.path.append('./lib/')
    # PYTHONPATH$B$K@_Dj$5$l$F$$$k(B ~/myWork/python/lib/stock_db.py $B$rFI$_9~$`$N$G!"0J2<$OITMW(B 
    # sys.path.append('/Users/popopopo/myWork/stock_info/perl_scripts/lib/')
    import stock_db
    import math
    import datetime

    # $B85%G!<%?$N%F!<%V%k$+$i%G!<%?$rDI2C$7!"DI2C8e$N%F!<%V%k$GCM$,%<%m$@$C$?>l9g$K=$@5$r2C$($k!#(B

    # $B=$@58e%F!<%V%k$N:G?7F|IU$H!"85%F!<%V%k$N:G?7F|IU$rHf3S$9$k(B
    # $B=$@58e%F!<%V%k$N:G?7F|IU$NJ}$,>.$5$1$l$P!"DI2C!&=$@5=hM}$r9T$&!#(B
    print """update zero value stock with non-zero value at the latest trading date\n\n"""
    # $BD>6a$NF|IU$r<hF@(B
    latestdateraw = stock_db.getLastDateFromTable(tblPriceDailyRaw)
    latestdate    = stock_db.getLastDateFromTable(tblPriceDaily)
    if (latestdate >= latestdateraw ):
        # $B=$@5$NI,MW$J$7(B
        print "no data to be inserted and updated on %s" % (tblPriceDaily)
        return None

    print "trading date to adjust : %s\n" % (latestdate)

    # $BD>6aF|IU$G3t2A$,%<%m$NLCJA!";T>l%3!<%I!"F|IU$r%;%C%H$K$7$?%?%W%k$N%j%9%H$r:n$k(B
    zeroStockList = getZeroValueStockList(tblPriceDailyRaw, latestdate)
    print "The number of stocks to be adjusted : (the same stock traded at different market will be double counted. : %s\n" % ( len(zeroStockList) )

    # $B%?%W%k%j%9%H$K$D$$$F%k!<%W(B
    for stockcd, marketcd, ymd in zeroStockList:
        # $BD>6a$NF|IU$+$i0lHV6a$$F|IU$G!"3t2A$,#0$G$O$J$$F|IU$N=*CM$r<hF@$9$k(B
        # memo : SQL$B$G#00J>e$NF|$rF|IU=g$KJB$SBX$($F!"0lHV>e$N%l%3!<%I$r$H$k!"$H$$$&J}K!$b;n$7$?$,!"(B
        # SQL$B$G%G!<%?$r<h$C$F$/$k$H$3$m$G;~4V$,$+$+$k$_$?$$$J$N$G!"$d$a(B
        # if stockcd != '3443' or marketcd != '6':
            # continue
        
        print "\nprocessing %s %s..." % (stockcd, marketcd)
        cur_date = ymd
        while(True):
            # $B%+%l%s%@!<$+$i0lF|A0$NF|IU$r<hF@$9$k(B
            prev_date = stock_db.getPrevTradingDate(cur_date)
            # $BA0<h0zF|$,B8:_$7$J$+$C$?$i!"L5;k$9$k(B
            if prev_date == None:
                print "no data available : stock code = %s  market code = %s" % (stockcd, marketcd)
                break
            prev_price = stock_db.getDailyStockPriceByCodeByDate(stockcd, marketcd, prev_date, 'close')

            # $B#1F|A0$N3t2A$,#0$@$C$?$i!"La$C$F$5$i$K#1F|A0$N3t2A$rD4$Y$k(B
            if prev_price <= 0 or prev_price==None:
                cur_date = prev_date

            # $B3t2A$,#00J>e$@$C$?$i$=$N3t2A$GCM$r99?7$9$k(B
            elif prev_price > 0:
                updateZeroPriceStock(stockcd, marketcd, ymd , prev_price)
                print "updated stock code = %s : market code = %s with value as of %s" % (stockcd, marketcd, prev_date)
                break
            else:
                print "something usual happen : stockcd = %s  market code = %s" % ( stockcd, marketcd)
                break


