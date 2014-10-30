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
    # PYTHONPATH$B$K@_Dj$5$l$F$$$k(B ~/myWork/python/lib/stock_db.py $B$rFI$_9~$`$N$G!"0J2<$OITMW(B 
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
    # $BJQ2=N(%F!<%V%k$N:G?7F|IU$r<hF@(B
    # $B#12sL\!J=i$a$F%F!<%V%k$K%G!<%?$rF~$l$k;~!K$OF|IU$r;XDj$7$F<B9T(B
    # latestdate = datetime.date(2001, 1, 4)
    latestdate = stock_db.getLastDateInStockChangeWeekly()

    # $BJQ2=N(%F!<%V%k$N:G?7F|IU$r4^$`F|IU%j%9%H$r<hF@(B
    datelist = stock_db.getWeeklyDateListAfter(latestdate, True)

    # $BJQ2=N($N7W;;$K$OFsF|J,$N%G!<%?$,I,MW$J$?$a!"F|IU%j%9%H$ND9$5$+$i#20z$/(B
    for i in range(len(datelist)-1):
        # print datelist[i],
        # $BD>6aFsF|J,$NA4LCJA$N3t2A%G!<%?$r<hF@$9$k(B
        # (stockcd, marketcd)$B$r%-!<$K$7$?%G!<%?$,J]B8$5$l$k!#3t2A%G!<%?$OF|IU$,?7$7$$=g$KJB$s$G$$$k!#(B
        # stockdata[(stockcd, marketcd)][column]$B$G%G!<%?$,J]B8$5$l$F$$$k!#(B
        stockdata = stock_db.getStockDataAllByDate(start=datelist[i], end=datelist[i+1], columns=['close'], tblStockPriceHist=stock_db.tblPriceWeekly)
        cnt = 0
        for code, mktcd in stockdata.keys():
        # for code, mktcd in cdlist:
            cnt+=1
            try:
                ret = round(stockdata[(code,mktcd)]['close'][0]/stockdata[(code,mktcd)]['close'][1]-1, 5)
                logret = round(math.log(stockdata[(code,mktcd)]['close'][0]/stockdata[(code,mktcd)]['close'][1]), 5)
            except ValueError:
                # log$B$N7W;;$G!"J,;R$,#0$K$J$k>l9g$K%(%i!<$K$J$k(B
                ret  = 0; logret = 0
            except ZeroDivisionError:
                ret  = 0; logret = 0
            except IndexError:
                # $B>e>lGQ;_$J$I$GFsF|J,$N%G!<%?$,<h$l$J$$$H$-$K%(%i!<$K$J$k(B
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
