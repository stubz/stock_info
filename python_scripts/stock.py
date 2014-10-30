# -*- coding: utf-8 -*-

import stock_db
from numpy import *

def getStockHistDailyByDate(mycur, start, end):
    sql = """select date, stockcd, marketcd, open, high, low, close, volume from stockPriceHistDaily  
             where date >= '%s' and date <= '%s' order by stockcd, date desc""" % (start, end) 
    # print sql
    mycur.execute(sql)
    data = mycur.fetchall()

    # save data into a hash
    stock = {}
    for row in data:
        stockKey = (row[1], row[2]) # tuple of ( stockCD, marketCD )
        stock.setdefault(stockKey, {})
        stock[stockKey].setdefault('date', [])
        stock[stockKey].setdefault('open', [])
        stock[stockKey].setdefault('high', [])
        stock[stockKey].setdefault('low', [])
        stock[stockKey].setdefault('close', [])
        stock[stockKey].setdefault('volume', [])
        # add data to arrays
        stock[stockKey]['date'].append(row[0])
        stock[stockKey]['open'].append(row[3])
        stock[stockKey]['high'].append(row[4])
        stock[stockKey]['low'].append(row[5])
        stock[stockKey]['close'].append(row[6])
        stock[stockKey]['volume'].append(row[7])

    # save data as numpy array object
    for cd in stock.keys():
        stock[cd]['date']   = array(stock[cd]['date'])
        stock[cd]['open']   = array(stock[cd]['open'])
        stock[cd]['high']   = array(stock[cd]['high'])
        stock[cd]['low']    = array(stock[cd]['low'])
        stock[cd]['close']  = array(stock[cd]['close'])
        stock[cd]['volume'] = array(stock[cd]['volume'])

    return stock 

def getNValue(stockData):
    """
    calculate N value for a stock
    stockData : hash of data
    """
    min_len = min(len(stockData['open']), len(stockData['high']), len(stockData['low']), len(stockData['close']))
    if min_len < 22: return 0
    # True Range
    # max(High - Low, High - PDC, PDC - Low) where PDC = previous day close
    return array([ stockData['high'][0:20] - stockData['low'][0:20],
            stockData['high'][0:20] - stockData['close'][1:21],
            stockData['close'][1:21] - stockData['low'][0:20] ]).max(axis=0).mean()

def getInitialNValue(mycur, stockcd, marketcd, N=20, min_rec = 73):
    """
    calculate the initial N value for the listed stock
    Initial value is crutial when calculating the exponentially weighted average.
    Then N values can be calculted as {19*N(t-1) + TR(t)}/20
    Approximately 3.45*(N+1) records are required to get 99.9% accurate value
    In this case, use 73 records
    """
    if stockcd == None or marketcd == None:
        return 0

    sql = """select date, stockcd, marketcd, open, high, low, close, volume from stockPriceHistDaily  
             where stockcd = '%s' and marketcd = '%s' order by date desc limit %d;""" % (start, end, min_rec) 
    mycur.execute(sql)
    data = mycur.fetchall()


def getDailyReturn(stockData, valtype):
    """
    valtype: open, high, low or close
    """
    if valtype != 'open' or valtype != 'high' or valtype != 'low' or valtype != 'close' :
        return 0
    else:
        return stockData[valtype][0]/stockData[valtype][1]-1

def getDailyReturnCts(stockData, valtype):
    """
    valtype: open, high, low or close
    """
    if valtype != 'open' or valtype != 'high' or valtype != 'low' or valtype != 'close' :
        return 0
    else:
        return log(stockData[valtype][0]/stockData[valtype][1])

################################################################################
################################################################################
################################################################################

# DB$B$+$i>pJs$r<h$C$F$/$k4X?t72(B

def getStockCodeListFromMSNMaster():
    """
    stockMasterMSN$B$+$iLCJA%3!<%I$N%j%9%H$r<h$C$F$/$k(B
    """

    cdlist = []

    con = stock_db.connect()
    sql = """ select stockcd, stockName, gyoshuCode from stockMasterMSN;"""

    con.query(sql)
    r = con.use_result()

    while(True):
        row = r.fetch_row(1,1)
        if not row: break
        cdlist.append((row[0]['stockcd'], row[0]['gyoshuCode']))

    con.close()
    return cdlist

def getStockZaimuFromMSN(stockcd, year):
    """
    stockZaimuMSN$B$+$i:bL3%G!<%?$r<hF@$9$k(B
    """

    if stockcd == None or year == None:
        return []

    zaimu = {}

    con = stock_db.connect()
    sql = """ select uriage, uriagesourieki, eigyorieki, zeikinmaejunrieki, zeihikigorieki,
            toukijunrieki, fusai, shihon, ryudoshisan, ryudofusai, shisan, shihonkei, 
            chokitoushi, uketoritegata, sonotakoteishisan, futsukabusu, eigyocf,
            toushicf, zaimucf from stockZaimuMSN
            where stockcd = '%s' and year = %s;""" % (stockcd, year)

    con.query(sql)
    r = con.use_result()

    try:
        zaimu = r.fetch_row(1,1)[0]
    except IndexError:
        # print "no data for stockcd = %s  year = %s" % (stockcd, year)
        raise
    except:
        # print "no data for stockcd = %s  year = %s" % (stockcd, year)
        raise

    con.close()
    return zaimu

def getStockPriceFromDailyTable(date, stockcd, marketcd):
    """
    $B;XDj$7$?F|IU!"LCJA%3!<%I!";T>l%3!<%I$+$i$=$NF|$N=*CM$r<hF@$7$FJV$9(B
    """

    if date==None or stockcd==None or marketcd==None:
        print "date, stockcode, marketcode must be specified."
        raise
        return 0

    sql = "select close from stockPriceHistDaily where stockcd='%s' and marketcd='%s' and date='%s'"
    con = stock_db.connect()
    con.query(sql % (stockcd, marketcd, date))
    r = con.use_result()

    try:
        val = r.fetch_row(1,1)[0]['close']
    except IndexError:
        # print "no data for stockcd = %s marketcd = %s date = %s" % (stockcd, marketcd, date)
        raise
    except:
        # print "no data for stockcd = %s marketcd = %s date = %s" % (stockcd, marketcd, date)
        raise

    con.close()
    return val
        
    




################################################################################
################################################################################
################################################################################

# $BJ,@O4X78$N4X?t72(B
def getTheoreticalStockValueSimple(net_operating_income, current_asset, current_debt, 
        other_asset, fixed_debt, shares, tax_rate, current_ratio, expected_return):

    """
    $B!V?7$7$$3t$NK\!W$G;H$o$l$F$$$k#13t$"$?$j2ACM$N4J0W7W;;J}K!(B
    net_operating_income : $B1D6HMx1W(B
    current_asset : $BN.F0;q;:(B
    current_debt  : $BN.F0Ii:D(B
    other_asset   : $BEj;q$=$NB>;q;:(B
    fixed_debt    : $B8GDjIi:D!JIi:D9g7W!<N.F0Ii:D$GJX59E*$K7W;;$7$F5a$a$?$b$N!K(B
    shares        : $B3t?t(B
    tax_rate      : $B@GN(!#=i4|CM(B40$B!s(B
    current_ratio : $BN.F0HfN(!a!JN.F0;q;:!K!`!JN.F0Ii:D!K(B
    expected_return : $B4|BT%j%?!<%s!#<+8J;qK\HfN($K1~$8$F7h$a$k(B
    """

    jigyo_kachi  = net_operating_income * ( 1 - tax_rate ) / expected_return
    zaisan_kachi = current_asset - (current_debt * current_ratio) + other_asset
    kigyo_kachi  = float(jigyo_kachi) + float(zaisan_kachi) - float(fixed_debt)
    try:
        stock_value = kigyo_kachi / shares
    except ZeroDivisionError:
        stock_value = 0
    except:
        stock_value = 0

    return stock_value










################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    import sys
    sys.path.append('/Users/popopopo/myWork/stock_info/perl_scripts/lib/')
    import stock_db
    
    con = stock_db.connect()
    cur = con.cursor()

    tmp = getStockHistDailyByDate(cur, '2009-09-01', '2009-10-01')

    print tmp['7203']['close'][0:10]
    
    cur.close()
    con.close()
