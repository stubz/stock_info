# -*- coding:utf-8 -*-

"""
priceDailyRawからデータを読み込んで、株価がゼロのところがあれば
前日（前日もゼロなら直近の０超の株価）株価で置き換える。
weekly, monthlyも作る。
"""

import MySQLdb
import stock_db
import sys
import math
import datetime

def deleteRecordsFromTableByDate(tbl, date):
    """
    指定した日付のデータを指定したテーブルから削除する
    """
    con = stock_db.connect()
    cur = con.cursor()
    
    sql = "delete from %s where date = '%s'" % (tbl, date)
    try:
        cur.execute(sql)
        # print "records as of %s has been deleted from %s" % ( date, tbl)
        con.commit()
        cur.close()
        con.close()
    except:
        print "failed to execute : \n%s" % (sql)
        cur.close()
        con.close()

def insertRecordsIntoTableByDate(srctbl, tgttbl, date):
    """
    指定した日付のデータをソーステーブルからターゲットテーブルに追加する。
    """
    con = stock_db.connect()
    cur = con.cursor()
    
    sql = "insert into %s select * from %s where date = '%s';" % (tgttbl, srctbl, date)
    try:
        cur.execute(sql)
        con.commit()
        # print "records as of %s has been inserted from %s into %s" % ( date, srctbl, tgttbl)
        cur.close()
        con.close()
    except:
        print "failed to execute : \n%s" % (sql)
        cur.close()
        con.close()

def getZeroValueStockList(tbl, date):
    """
    株価がゼロの銘柄のコード、市場コード、日付のタプルをリストに保存する
    """
    con = stock_db.connect()

    # 始値、高値、安値、終値、取引高の中からどの項目を取得するか指定する。
    # どの項目にもマッチしない場合は終値だけ返す
    
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

def checkZeroValueStock(tbl, stockcd, marketcd, date):
    """
    指定した日付以前の株価が全てゼロかどうかをチェックする
    """
    con = stock_db.connect(); cur = con.cursor()
    sql = "select sum(close) from %s where stockcd = '%s' and marketcd = '%s' and date<'%s';" % (tbl, stockcd, marketcd, date)
    try:
        cur.execute(sql)
        totval = cur.fetchall()[0][0]
        cur.close(); con.close()
    except MySQLdb.OperationalError, e:
        print "sql が失敗したよ。: %s " % ( sql )
        print e[1]
        totval = 1
        cur.close(); con.close()
    except:
        print "failed to get data"
        cur.close(); con.close()
        totval = 1

    if totval == 0:
        return True
    else:
        return False

# 
def updateZeroPriceStock(tbl, stockcd, marketcd, date, price):
    """
    株価が０だった銘柄の株価を修正する。終値以外も全て同じ値にして、取引高はゼロにする
    """
    con = stock_db.connect()
    sql = """update %s set open=%s, high=%s, low=%s, close = %s, volume=0
            where stockcd = '%s' and marketcd = '%s' and date='%s'""" % (tbl, price, price, price, price, stockcd, marketcd, date )
    # print sql
    try:
        con.query(sql)
        con.commit()
        con.close()
    except:
        print "sql failed : %s" % (sql)
        con.close()

def updateZeroValueStockList(zerolist):
    """
    (銘柄コード、市場コード、日付）のタプルを読み込んで、
    株かがゼロになっているレコードについて直近のゼロ超の値に置き換えて更新する
    メモ：priceDailyテーブルで前日が０だったら、それ以上さかのぼっても全てゼロという意味なので、しないように変更した。
        ：oldとついたプログラムはwhileループを使っているが、それを廃止したバージョン。最初の取引日のチェックなども廃止。
    """

    # タプルリストについてループ
    for stockcd, marketcd, ymd in zerolist:
        # 直近の日付から一番近い日付で、株価が０ではない日付の終値を取得する
        # print "processing %s %s..." % (stockcd, marketcd)
        cur_date = ymd
        
        # カレンダーから一日前の日付を取得する
        prev_date = stock_db.getPrevTradingDate(cur_date)
        # 前取引日が存在しなかったら、無視する
        if prev_date == None:
            print "no data available as of the previous date of %s : stock code = %s  market code = %s" % (cur_date, stockcd, marketcd)
            continue
        prev_price = stock_db.getDailyStockPriceByCodeByDate(stockcd, marketcd, prev_date, 'close')

        # １日前の株価が０だったら、戻ってさらに１日前の株価を調べる
        # !!!!!! 2010/09/24 : 前日が０だと、その前をさかのぼってもゼロのはずなので、１日前にさらにさかのぼる処理は止める
        # 代わりに、何もしない。
        if prev_price <= 0 or prev_price==None:
            # cur_date = prev_date
            print "stockcd = %s marketcd = %s : zero value for %s. ignored" % (stockcd, marketcd, prev_date)

        # 株価が０以上だったらその株価で値を更新する
        elif prev_price > 0:
            updateZeroPriceStock(stock_db.tblPriceDaily, stockcd, marketcd, ymd , prev_price)
            # print "updated stock code = %s : market code = %s with value as of %s" % (stockcd, marketcd, prev_date)
        else:
            print "something unusual happened : stockcd = %s  market code = %s" % ( stockcd, marketcd)
            pass

def updateZeroValueStockListWeekly(zerolist):
    """
    (銘柄コード、市場コード、日付）のタプルを読み込んで、
    株かがゼロになっているレコードについて直近のゼロ超の値に置き換えて更新する
    """

    # タプルリストについてループ
    for stockcd, marketcd, ymd in zerolist:
        # 直近の日付から一番近い日付で、株価が０ではない日付の終値を取得する
        # print "processing %s %s..." % (stockcd, marketcd)
        cur_date = ymd
        
        # カレンダーから一日前の日付を取得する
        prev_date = stock_db.getPrevTradingDateWeekly(cur_date)
        # 前取引日が存在しなかったら、無視する
        if prev_date == None:
            print "no data available as of the previous date of %s : stock code = %s  market code = %s" % (cur_date, stockcd, marketcd)
            continue
        prev_price = stock_db.getDailyStockPriceByCodeByDate(stockcd, marketcd, prev_date, 'close')

        # １日前の株価が０だったら、戻ってさらに１日前の株価を調べる
        # !!!!!! 2010/09/24 : 前日が０だと、その前をさかのぼってもゼロのはずなので、１日前にさらにさかのぼる処理は止める
        # 代わりに、何もしない。
        if prev_price <= 0 or prev_price==None:
            # cur_date = prev_date
            print "stockcd = %s marketcd = %s : zero value for %s. ignored" % (stockcd, marketcd, prev_date)

        # 株価が０以上だったらその株価で値を更新する
        elif prev_price > 0:
            updateZeroPriceStock(stock_db.tblPriceWeekly, stockcd, marketcd, ymd , prev_price)
            # print "updated stock code = %s : market code = %s with value as of %s" % (stockcd, marketcd, prev_date)
        else:
            print "something unusual happened : stockcd = %s  market code = %s" % ( stockcd, marketcd)
            pass

def updateZeroValueStockList_old(zerolist):
    """
    (銘柄コード、市場コード、日付）のタプルを読み込んで、
    株かがゼロになっているレコードについて直近のゼロ超の値に置き換えて更新する
    """

    # タプルリストについてループ
    for stockcd, marketcd, ymd in zerolist:
        # 直近の日付から一番近い日付で、株価が０ではない日付の終値を取得する
        # print "processing %s %s..." % (stockcd, marketcd)
        cur_date = ymd
        # 指定した日付以前の株価が全てゼロだったら無視する
        if checkZeroValueStock(stock_db.tblPriceDailyRaw, stockcd, marketcd, ymd):
            print "stockcd = %s  marketcd = %s will be skipped : all records have zero value since the initial data."
            continue
        
        # テーブルにある最初の取引日を取得する
        firstTradingDate = stock_db.getFirstTradingDateByStock(stockcd, marketcd)

        while(True):
            # 最初の取引日までさかのぼってしまったら無視する
            if cur_date <= firstTradingDate:
                print "stockcd = %s  marketcd = %s : all records have zero value since the initial data, thus not updated" % (stockcd, marketcd)
                break
            # カレンダーから一日前の日付を取得する
            prev_date = stock_db.getPrevTradingDate(cur_date)
            # 前取引日が存在しなかったら、無視する
            if prev_date == None:
                # print "no data available : stock code = %s  market code = %s" % (stockcd, marketcd)
                break
            prev_price = stock_db.getDailyStockPriceByCodeByDate(stockcd, marketcd, prev_date, 'close')

            # １日前の株価が０だったら、戻ってさらに１日前の株価を調べる
            # !!!!!! 2010/09/24 : 前日が０だと、その前をさかのぼってもゼロのはずなので、１日前にさらにさかのぼる処理は止める
            # 代わりに、何もしない。
            if prev_price <= 0 or prev_price==None:
                # cur_date = prev_date
                print "stockcd = %s marketcd = %s : no data for %s. ignored" % (stockcd, marketcd, prev_date)
                break

            # 株価が０以上だったらその株価で値を更新する
            elif prev_price > 0:
                updateZeroPriceStock(stock_db.tblPriceDaily, stockcd, marketcd, ymd , prev_price)
                # print "updated stock code = %s : market code = %s with value as of %s" % (stockcd, marketcd, prev_date)
                break
            else:
                # print "something unusual happened : stockcd = %s  market code = %s" % ( stockcd, marketcd)
                break

def updatePriceDailyTable():
    # Rawデータの日付とpriceDailyテーブルの最新日付を調べる
    print """\n *** update zero value stock from priceDaily with non-zero value at the latest trading date ***\n"""
    latestdateraw = stock_db.getLastDateFromTable(stock_db.tblPriceDailyRaw)
    latestdate    = stock_db.getLastDateFromTable(stock_db.tblPriceDaily)
    # priceDailyテーブルが空だったときは、一番初めのデータ日付を使う
    if latestdate==None:
        latestdate = stock_db.getFirstDateFromTable(stock_db.tblPriceDailyRaw)

    # １日ずつ最新日付がRawテーブルと同じになるまで処理をする
    while latestdate <= latestdateraw:
        
        print "\n****** start processing records as of %s *******\n" % (latestdate) 

        # 指定した日付のデータをpriceDailyテーブルから削除する
        deleteRecordsFromTableByDate(stock_db.tblPriceDaily, latestdate)

        # 指定した日付のデータをRawテーブルからpriceDailyテーブルに追加
        insertRecordsIntoTableByDate(srctbl=stock_db.tblPriceDailyRaw, tgttbl=stock_db.tblPriceDaily, date=latestdate)

        # 追加したデータについて、株価がゼロの銘柄コード、市場コード、日付のリストを作る
        zeroStockList = getZeroValueStockList(stock_db.tblPriceDaily, latestdate)
        print "The number of stocks to be adjusted : %s\n (the same stock traded at different market will be double counted.) \n" % ( len(zeroStockList) )

        # 株価ゼロのリストについて、データの更新を行う
        updateZeroValueStockList(zeroStockList)

        # 途中経過のプリント
        print("\n%s\n" % ("*"*80))
        print("%s : records as of %s has been processed." %(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), latestdate) )

        # ループ用に翌取引日を指定する。
        latestdate = stock_db.getNextTradingDate(latestdate)
        # 日付がない場合（最後のときには必ずなってしまう）、止める
        if latestdate == None:
            break

    # --- while loop の終了 --- #      

def updatePriceWeeklyTable():
    # Rawデータの日付とpriceWeeklyテーブルの最新日付を調べる
    print """\n *** update zero value stock from priceWeekly with non-zero value at the latest trading date ***\n"""
    latestdateraw = stock_db.getLastDateFromTable(stock_db.tblPriceWeeklyRaw)
    latestdate    = stock_db.getLastDateFromTable(stock_db.tblPriceWeekly)
    # priceWeeklyテーブルが空だったときは、一番初めのデータ日付を使う
    if latestdate==None:
        latestdate = stock_db.getFirstDateFromTable(stock_db.tblPriceWeeklyRaw)

    # １日ずつ最新日付がRawテーブルと同じになるまで処理をする
    while latestdate <= latestdateraw:
        
        print "\n****** start processing records as of %s *******\n" % (latestdate) 

        # 指定した日付のデータをpriceWeeklyテーブルから削除する
        deleteRecordsFromTableByDate(stock_db.tblPriceWeekly, latestdate)

        # 指定した日付のデータをRawテーブルからpriceWeeklyテーブルに追加
        insertRecordsIntoTableByDate(srctbl=stock_db.tblPriceWeeklyRaw, tgttbl=stock_db.tblPriceWeekly, date=latestdate)

        # 追加したデータについて、株価がゼロの銘柄コード、市場コード、日付のリストを作る
        zeroStockList = getZeroValueStockList(stock_db.tblPriceWeekly, latestdate)
        print "The number of stocks to be adjusted : %s\n (the same stock traded at different market will be double counted.) \n" % ( len(zeroStockList) )

        # 株価ゼロのリストについて、データの更新を行う
        updateZeroValueStockList(zeroStockList)

        # 途中経過のプリント
        print("\n%s\n" % ("*"*80))
        print("%s : records as of %s has been processed." %(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), latestdate) )

        # ループ用に翌取引日を指定する。
        latestdate = stock_db.getNextTradingDateWeekly(latestdate)
        # 日付がない場合（最後のときには必ずなってしまう）、止める
        if latestdate == None:
            break

    # --- while loop の終了 --- #      

#----------------------------------------------------------------------------------------------------#

if  __name__ == '__main__':
    # updatePriceDailyTable() 
    updatePriceWeeklyTable()
