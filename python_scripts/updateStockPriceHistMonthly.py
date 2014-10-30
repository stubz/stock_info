#-*- coding:utf-8 -*-
#
# 月次データを作成する。
#
import stock_db
import datetime

def getMaxMinDateFromStockPriceHistDaily():
    """
    日付の最初と最後を取得。
    """
    con = stock_db.connect(); cur = con.cursor()
    sql = "select min(date), max(date) from %s" % (stock_db.tblPriceDaily)
    try:
        cur.execute(sql)
        mindate, maxdate = cur.fetchall()[0][0:2]
        cur.close(); con.close()
        return (mindate, maxdate)
    except:
        print "failed to get date list from %s" % (stock_db.tblPriceDaily)
        cur.close(); con.close()
        return None


def getMaxDateFromStockPriceHistMonthly():
    """
    日付の最初と最後を取得。
    """
    con = stock_db.connect(); cur = con.cursor()
    sql = "select max(date) from %s" % (stock_db.tblPriceMonthly)
    try:
        cur.execute(sql)
        maxdate = cur.fetchall()[0][0]
        cur.close(); con.close()
        return maxdate
    except:
        print "failed to get date list from %s" % (stock_db.tblPriceMonthly)
        cur.close(); con.close()
        return None



def getEndOfMonthDateList(start):
    """
    startで指定した日付以降の月末日のリストを作る
    """
    con = stock_db.connect(); cur = con.cursor()
    sql = """
            select max(a.date) as date, a.yyyymm from
            (select date, year(date)*100+month(date) as yyyymm from %s
                where date >= '%s') a
            group by a.yyyymm;
          """ % (stock_db.tblCalendarDaily, start)
    try:
        cur.execute(sql)
        res = cur.fetchall()
        cur.close(); con.close()
    except:
        print "failed to get date list from %s" % (stock_db.tblCalendarDaily)
        cur.close(); con.close()
        return None

    datelist = [x[0] for x in res]
    return datelist

def insertDataIntoStockPriceHistMonthly(date):
    """
    指定した日付のデータを月次テーブルに追加する
    """
    con = stock_db.connect(); cur = con.cursor()
    sql = """INSERT INTO %s
            SELECT date, stockcd, marketcd, open, high, low, close, volume from %s
            WHERE date = '%s'
          """ % (stock_db.tblPriceMonthly, stock_db.tblPriceDaily, date)

    try:
        cur.execute(sql)
        con.commit()
        cur.close(); con.close()
        print "inserted %s data ..." % (date)
    except:
        print "failed to insert %s data \n%s" % (date, sql)
        con.rollback()
        cur.close(); con.close()

def insertDateIntoCalendarMonthly(date):
    """
    日付をcalendarMonthlyに追加する
    """
    con = stock_db.connect(); cur = con.cursor()
    sql = """INSERT INTO %s (date) VALUES('%s');""" % (stock_db.tblCalendarMonthly, date)

    try:
        cur.execute(sql)
        con.commit()
        cur.close(); con.close()
        print "inserted date value %s into %s ..." % (date, stock_db.tblCalendarMonthly)
    except:
        print "failed to insert date %s into %s\n%s" % (date, stock_db.tblCalendarMonthly, sql)
        con.rollback()
        cur.close(); con.close()


####################################################################################################

if __name__=='__main__':

    # 日次データテーブルから最初と最後の日付リストを作る(初めて作成するときのみ）
    # startdate, endate = getMaxMinDateFromStockPriceHistDaily()
    # ２回目以降は、priceMonthlyから最後の日付を取得する
    startdate = getMaxDateFromStockPriceHistMonthly()
    #
    # 月末日のリストを作る
    datelist = getEndOfMonthDateList(startdate)
    # 当月分の日付は抜きとる(最後の要素を取り除く）
    datelist = datelist[1:-1]
    # print datelist
    # 月末日のリストを使って、日次テーブルからデータを順に取得する
    for date in datelist:
        # 株かデータの追加
        insertDataIntoStockPriceHistMonthly(date)
        # 日付をカレンダーに追加
        insertDateIntoCalendarMonthly(date)

