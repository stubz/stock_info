# -*- coding:utf-8 -*-
# 値がつかない場合株価がOで登録される。そのためにボラティリティー計算などで使用できない。
# ゼロの場合は直近のゼロ超の日付の株価で洗い替える
#
import stock_db

# テーブル名
tblPriceDailyRaw   = 'priceDailyRaw'
tblPriceDaily      = 'priceDaily'
tblPriceWeeklyRaw  = 'priceWeeklyRaw'
tblPriceWeekly     = 'priceWeekly'
tblPriceMonthlyRaw = 'priceMonthlyRaw'
tblPriceMonthly    = 'priceMonthly'

def getZeroValueStockList(tbl, date):
    """
    株価がゼロの銘柄のコード、市場コード、日付のタプルをリストに保存する
    """
    con = stock_db.connect()

    # 始値、高値、安値、終値、取引高の中からどの項目を取得するか指定する。
    # どの項目にもマッチしない場合は終値だけ返す
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
        # 銘柄コードと市場コード日付をキーにしてデータをdictionaryに保存する
        stockKey  = (data['stockcd'], data['marketcd'], date)
        stockdata.append(stockKey)

    con.close()
    return stockdata

def getLatestNonZeroPrice(stockcd, marketcd, date):
    """
    直近の日付から一番近い日付で、株価が０ではない日付の終値を取得する
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
    株価が０だった銘柄の終値だけ修正する
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
    # PYTHONPATHに設定されている ~/myWork/python/lib/stock_db.py を読み込むので、以下は不要 
    # sys.path.append('/Users/popopopo/myWork/stock_info/perl_scripts/lib/')
    import stock_db
    import math
    import datetime

    # 元データのテーブルからデータを追加し、追加後のテーブルで値がゼロだった場合に修正を加える。

    # 修正後テーブルの最新日付と、元テーブルの最新日付を比較する
    # 修正後テーブルの最新日付の方が小さければ、追加・修正処理を行う。
    print """update zero value stock with non-zero value at the latest trading date\n\n"""
    # 直近の日付を取得
    latestdateraw = stock_db.getLastDateFromTable(tblPriceDailyRaw)
    latestdate    = stock_db.getLastDateFromTable(tblPriceDaily)
    if (latestdate >= latestdateraw ):
        # 修正の必要なし
        print "no data to be inserted and updated on %s" % (tblPriceDaily)
        return None

    print "trading date to adjust : %s\n" % (latestdate)

    # 直近日付で株価がゼロの銘柄、市場コード、日付をセットにしたタプルのリストを作る
    zeroStockList = getZeroValueStockList(tblPriceDailyRaw, latestdate)
    print "The number of stocks to be adjusted : (the same stock traded at different market will be double counted. : %s\n" % ( len(zeroStockList) )

    # タプルリストについてループ
    for stockcd, marketcd, ymd in zeroStockList:
        # 直近の日付から一番近い日付で、株価が０ではない日付の終値を取得する
        # memo : SQLで０以上の日を日付順に並び替えて、一番上のレコードをとる、という方法も試したが、
        # SQLでデータを取ってくるところで時間がかかるみたいなので、やめ
        # if stockcd != '3443' or marketcd != '6':
            # continue
        
        print "\nprocessing %s %s..." % (stockcd, marketcd)
        cur_date = ymd
        while(True):
            # カレンダーから一日前の日付を取得する
            prev_date = stock_db.getPrevTradingDate(cur_date)
            # 前取引日が存在しなかったら、無視する
            if prev_date == None:
                print "no data available : stock code = %s  market code = %s" % (stockcd, marketcd)
                break
            prev_price = stock_db.getDailyStockPriceByCodeByDate(stockcd, marketcd, prev_date, 'close')

            # １日前の株価が０だったら、戻ってさらに１日前の株価を調べる
            if prev_price <= 0 or prev_price==None:
                cur_date = prev_date

            # 株価が０以上だったらその株価で値を更新する
            elif prev_price > 0:
                updateZeroPriceStock(stockcd, marketcd, ymd , prev_price)
                print "updated stock code = %s : market code = %s with value as of %s" % (stockcd, marketcd, prev_date)
                break
            else:
                print "something usual happen : stockcd = %s  market code = %s" % ( stockcd, marketcd)
                break


