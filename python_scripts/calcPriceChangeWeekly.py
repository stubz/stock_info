# -*- coding:utf-8 -*-
import stock_db

# not in use 
class Storage(dict):
    def __getattr__(self, key): 
        if self.has_key(key): 
            return self[key]
        raise AttributeError, repr(key)
    def __setattr__(self, key, value): 
        self[key] = value
    def __repr__(self):     
        return '<Storage ' + dict.__repr__(self) + '>'
# end of not in use

####################################################################################################

if __name__=='__main__':
    import sys
    # sys.path.append('./lib/')
    # PYTHONPATHに設定されている ~/myWork/python/lib/stock_db.py を読み込むので、以下は不要 
    # sys.path.append('/Users/popopopo/myWork/stock_info/perl_scripts/lib/')
    import stock_db
    import math
    import datetime

    print("\n\n%s\n\n" % ("*"*80))
    print("******* calculate daily price change from %s *******\n\n" % (stock_db.tblPriceDaily))

    con = stock_db.connect()
    cur = con.cursor()

    # get list of stock code
    cdlist = stock_db.getStockCodeListCurrent()
    # get a list of dates
    # 変化率テーブルの最新日付を取得
    # １回目（初めてテーブルにデータを入れる時）は日付を指定して実行
    # latestdate = datetime.date(2001, 1, 4)
    latestdate = stock_db.getLastDateInStockChangeWeekly()

    # 変化率テーブルの最新日付を含む日付リストを取得
    datelist = stock_db.getWeeklyDateListAfter(latestdate, True)

    # 変化率の計算には二日分のデータが必要なため、日付リストの長さから２引く
    for i in range(len(datelist)-1):
        # print datelist[i],
        # 直近二日分の全銘柄の株価データを取得する
        # (stockcd, marketcd)をキーにしたデータが保存される。株価データは日付が新しい順に並んでいる。
        # stockdata[(stockcd, marketcd)][column]でデータが保存されている。
        stockdata = stock_db.getStockDataAllByDate(start=datelist[i], end=datelist[i+1], columns=['close'], tblStockPriceHist=stock_db.tblPriceWeekly)
        cnt = 0
        for code, mktcd in stockdata.keys():
        # for code, mktcd in cdlist:
            cnt+=1
            try:
                ret = round(stockdata[(code,mktcd)]['close'][0]/stockdata[(code,mktcd)]['close'][1]-1, 5)
                logret = round(math.log(stockdata[(code,mktcd)]['close'][0]/stockdata[(code,mktcd)]['close'][1]), 5)
            except ValueError:
                # logの計算で、分子が０になる場合にエラーになる
                ret  = 0; logret = 0
            except ZeroDivisionError:
                ret  = 0; logret = 0
            except IndexError:
                # 上場廃止などで二日分のデータが取れないときにエラーになる
                print "not complete data: date=%s stockcd=%s marketcd=%s" % (datelist[i+1], code, mktcd)
                ret  = 0; logret = 0
                
            sql = """INSERT INTO %s (date, stockcd, marketcd, ret, logret) 
                values('%s', '%s', '%s', %f, %f)""" % (stock_db.tblPriceChangeWeekly, datelist[i+1], code, mktcd, ret, logret)
            try:
                cur.execute(sql)
            except:
                print "failed to execute\ndate=%s\tstockcd=%s\tmarketcd=%s\nsql :\n%s" % (datelist[i],code, mktcd,sql)

            # commit by transaction by every 1000 records
            if cnt % 1000 == 0:
                con.commit()
        
        con.commit()
        print "%s data processed.." % (datelist[i+1])
        
    cur.close()
    con.close()
