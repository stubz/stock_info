# -*- coding: utf-8 -*-
"""
Yahoo! Finance から連結の決算情報を取得する。
直近３年分のデータを取得できる。
データがEUCで保存されている前提（次期バージョンの改善点。簡単に文字コードの類推をするモジュールがあるらしい）

データ更新では１年分だけで十分だが、そこは毎回手で直す必要がある。
"""
import re, datetime, urllib2, sys
from BeautifulSoup import BeautifulSoup          # For processing HTML
from HTMLParser import HTMLParseError
sys.path.append('/Users/popopopo/myWork/python/lib')
# sys.path.append('./lib/')
import stock_db
from stockMSN import getStockCodeListFromMSN, getStockGyoshuListFromMSN
from mysoup import get_soup  # BeautifulSoupを改良して、日本語ページでもエラーなく処理できるようにしたもの

# 日本語文字とマッチさせる正規表現
# http://programmer-toy-box.sblo.jp/category/520539-1.html
# 
nihongo_regex = re.compile(r'[^\x20-\x7E]')
# HTMLのコメント行を削除する正規表現
re_word = re.compile( r"<!--.*?-->",re.DOTALL )

# 数値データとマッチさせる正規表現
# numRegex = re.compile('\d+(\.*|\,*)\d+')
num_regex = re.compile(r'[^0-9\.\-]')
hyphen_regex = re.compile(r'---')


################################################################################

def getPSData(stockcd):
    """
    MSNの財務諸表ページから、PSのデータを抜き出す
    stockcd : 4-digit stock code
    二次元配列を返す。値は、１行目に2009, 2008 など直近５年の年のリスト
    １列目は科目名等の不要な項目で、２列目以降に各年の数字が入っている
    """

    # 損益計算書
    url_ps = "http://jp.moneycentral.msn.com/investor/invsub/results/statemnt.aspx?symbol=JP:%s"

    # 銘柄コードで指定した銘柄のデータをダウンロードして処理する
    data = urllib2.urlopen(url_ps % stockcd).read()
        
    # データを保存するための配列。最終的には二次元の配列にする
    ps_data = []

    # 取得する財務データエリアの取得
    ps = get_soup(data).find('table',{'class':'ftable'})
    # 財務データの年数を取る
    # 2009 2008 2007 等と入っている。初めの列はスペースだが、とりあえずそのまま読み込んでおく
    trr1 = ps.find('tr', {'class':'r1'})
    year_arr = []
    for num, td in enumerate(trr1.findAll('td')):
        try:
            year_arr.append( int(td.contents[0]) )
        except ValueError:
            year_arr.append(0)
    ps_data.append( year_arr )

    # PSの主要項目だけ抽出する
    # 売上高合計、売上総利益、営業利益、税金等調整前当期純利益、
    # 税引き後利益、異常項目前の当期純利益
    for trft1 in ps.findAll('tr', {'class':'ft1'}):
        # １行分のデータ(１科目の過去履歴)を保存するための配列
        ps_contents = []
        for td in trft1.findAll('td'):
            # 営業利益、など、項目名のエリアと、データが入っている列を区別する
            try:
                ps_contents.append( td.find('span').contents[0] )
            except:
                try:
                    # 数字に千区切りのコンマなどある場合があるので、それを取り除く
                    ps_contents.append( int( num_regex.sub('', td.contents[0] ) ) )
                except ValueError:
                    ps_contents.append(0)

        # 過去のデータは一行のデータになっているので、配列ごと保存用配列追加して二次元配列を作る
        ps_data.append( ps_contents )
 
    return ps_data

def getBSData(stockcd):
    """
    MSNの財務諸表ページから、BSのデータを抜き出す
    stockcd : 4-digit stock code
    二次元配列を返す。値は、１行目に2009, 2008 など直近５年の年のリスト
    １列目は科目名等の不要な項目で、２列目以降に各年の数字が入っている
    """

    # 損益計算書
    url = "http://jp.moneycentral.msn.com/investor/invsub/results/statemnt.aspx?symbol=JP:%s"
    url_bs = url + "&lstStatement=Balance&stmtView=Ann"

    # 銘柄コードで指定した銘柄のデータをダウンロードして処理する
    data = urllib2.urlopen(url_bs % stockcd).read()
        
    # データを保存するための配列。最終的には二次元の配列にする
    bs_data = []

    # 取得する財務データエリアの取得
    bs = get_soup(data).find('table',{'class':'ftable'})
    # 財務データの年数を取る
    # 2009 2008 2007 等と入っている。初めの列はスペースだが、とりあえずそのまま読み込んでおく
    trr1 = bs.find('tr', {'class':'r1'})
    year_arr = []
    for num, td in enumerate(trr1.findAll('td')):
        try:
            year_arr.append( int(td.contents[0]) )
        except ValueError:
            year_arr.append(0)
    bs_data.append( year_arr )

    # BSの主要項目だけ抽出する
    # 負債合計、資本合計、流動資産合計、流動負債合計、資産合計、負債・少数株主持ち分及び資本合計
    # 普通株式発行数合計（百万）
    for trft1 in bs.findAll('tr', {'class':'ft1'}):
        # １行分のデータ(１科目の過去履歴)を保存するための配列
        bs_contents = []
        for td in trft1.findAll('td'):
            # 負債合計、資本合計の取得
            try:
                bs_contents.append( td.find('span').contents[0] )
            except:
                try:
                    # 数字に千区切りのコンマなどある場合があるので、それを取り除く
                    bs_contents.append( int( num_regex.sub('', td.contents[0] ) ) )
                except ValueError:
                    bs_contents.append(0)

        # 過去のデータは一行のデータになっているので、配列ごと保存用配列追加して二次元配列を作る
        bs_data.append( bs_contents )

    for trft2 in bs.findAll('tr', {'class':'ft2'}):
        # １行分のデータ(１科目の過去履歴)を保存するための配列
        bs_contents = []
        for td in trft2.findAll('td'):
            # 流動資産合計、流動負債合計の取得
            try:
                bs_contents.append( td.find('span').contents[0] )
            except:
                try:
                    # 数字に千区切りのコンマなどある場合があるので、それを取り除く
                    bs_contents.append( int( num_regex.sub('', td.contents[0] ) ) )
                except ValueError:
                    bs_contents.append(0)
        # 過去のデータは一行のデータになっているので、配列ごと保存用配列追加して二次元配列を作る
        bs_data.append( bs_contents )

    for trft3 in bs.findAll('tr', {'class':'ft3'}):
        # １行分のデータ(１科目の過去履歴)を保存するための配列
        bs_contents = []
        for td in trft3.findAll('td'):
            # 資産合計、負債、少数株主持ち分及び資本合計
            try:
                bs_contents.append( td.find('span').contents[0] )
            except:
                try:
                    # 数字に千区切りのコンマなどある場合があるので、それを取り除く
                    bs_contents.append( int( num_regex.sub('', td.contents[0] ) ) )
                except ValueError:
                    bs_contents.append(0)
        # 過去のデータは一行のデータになっているので、配列ごと保存用配列追加して二次元配列を作る
        bs_data.append( bs_contents )

    for num, trfd1 in enumerate(bs.findAll('tr', {'class':'fd1'})):
        # １行分のデータ(１科目の過去履歴)を保存するための配列
        bs_contents = []
        # 長期投資、受取手形、その他固定資産だけを取り出し、投資その他資産を取得する
        if num >= 7 and num <=9:
            for td in trfd1.findAll('td'):
                # 項目名のエリアと、データが入っている列を区別する
                try:
                    bs_contents.append( td.find('span').contents[0] )
                except:
                    try:
                        bs_contents.append( int(num_regex.sub('', td.contents[0])) )
                    except ValueError:
                        bs_contents.append(0)
            # 過去のデータは一行のデータになっているので、配列ごと保存用配列追加して二次元配列を作る
            bs_data.append( bs_contents )

    # 株数
    for trft5 in bs.findAll('tr', {'class':'fd5'}):
        # １行分のデータ(１科目の過去履歴)を保存するための配列
        bs_contents = []
        for td in trft5.findAll('td'):
            # 普通株式発行株数
            try:
                bs_contents.append( td.find('span').contents[0] )
            except:
                try:
                    # 数字に千区切りのコンマなどある場合があるので、それを取り除く
                    bs_contents.append( int( num_regex.sub('', td.contents[0] ) ) )
                except ValueError:
                    bs_contents.append(0)
        # 過去のデータは一行のデータになっているので、配列ごと保存用配列追加して二次元配列を作る
        bs_data.append( bs_contents )

    return bs_data

def getCFData(stockcd):
    """
    MSNの財務諸表ページから、CFのデータを抜き出す
    stockcd : 4-digit stock code
    二次元配列を返す。値は、１行目に2009, 2008 など直近５年の年のリスト
    １列目は科目名等の不要な項目で、２列目以降に各年の数字が入っている
    """

    # 損益計算書
    url = "http://jp.moneycentral.msn.com/investor/invsub/results/statemnt.aspx?symbol=JP:%s"
    url_cf = url + "&lstStatement=CashFlow&stmtView=Ann"

    # 銘柄コードで指定した銘柄のデータをダウンロードして処理する
    data = urllib2.urlopen(url_cf % stockcd).read()
        
    # データを保存するための配列。最終的には二次元の配列にする
    cf_data = []

    # 取得する財務データエリアの取得
    cf = get_soup(data).find('table',{'class':'ftable'})
    # 財務データの年数を取る
    # 2009 2008 2007 等と入っている。初めの列はスペースだが、とりあえずそのまま読み込んでおく
    trr1 = cf.find('tr', {'class':'r1'})
    year_arr = []
    for td in trr1.findAll('td'):
        try:
            year_arr.append( int(td.contents[0]) )
        except ValueError:
            year_arr.append(0)
    cf_data.append( year_arr )

    # CFの主要項目だけ抽出する
    # 営業CF 投資CF 財務CF
    for trft1 in cf.findAll('tr', {'class':'ft1'}):
        # １行分のデータ(１科目の過去履歴)を保存するための配列
        cf_contents = []
        for td in trft1.findAll('td'):
            # 営業利益、など、項目名のエリアと、データが入っている列を区別する
            try:
                cf_contents.append( td.find('span').contents[0] )
            except:
                try:
                    # 数字に千区切りのコンマなどある場合があるので、それを取り除く
                    cf_contents.append( int( num_regex.sub('', td.contents[0] ) ) )
                except ValueError:
                    cf_contents.append(0)

        # 過去のデータは一行のデータになっているので、配列ごと保存用配列追加して二次元配列を作る
        cf_data.append( cf_contents )
 
    return cf_data

def get10YearSummaryData(stockcd):
    """
    MSNの財務諸表ページから、直近１０年間の主要財務データを抜き出す
    stockcd : 4-digit stock code
    二次元配列を返す。値は、１行目に売上げ、金利税引き前利益 のリスト
    １列目は年月、２列目以降に各年の数字が入っている
    """

    # 損益計算書
    url = "http://jp.moneycentral.msn.com/investor/invsub/results/statemnt.aspx?symbol=JP:%s"
    # １０年間の概括
    url_smry = url + "&lstStatement=10YearSummary&stmtView=Ann"

    # 銘柄コードで指定した銘柄のデータをダウンロードして処理する
    data = urllib2.urlopen(url_smry % stockcd).read()
        
    # データを保存するための配列。最終的には二次元の配列にする
    smry_data = []

    # 取得する財務データエリアの取得
    smry_ps = get_soup(data).find('table',{'id':'INCS'})
    smry_bs = get_soup(data).find('table',{'id':'BALS'})

    # 財務データの項目名は無視して、データだけ取る

    # PS
    # 左から、
    # 売上げ、金利税引き前利益、減価償却、純利益、１株益、税率（％）の順
    for num, tr in enumerate(smry_ps.findAll('tr')):
        # header行は無視する
        if num == 0:
            continue
        # データを保存するための配列
        ps_contents = []
        for td in tr.findAll('td'):
            try:
                ps_contents.append( float( num_regex.sub('', td.contents[0]) ) )
            except ValueError:
                ps_contents.append( num_regex.sub('', td.contents[0]) ) 
        smry_data.append(ps_contents)

    # BS
    for num, tr in enumerate(smry_bs.findAll('tr')):
        # headerの行は無視する
        if num == 0:
            continue
        # データを保存するための配列
        bs_contents = []
        for td in tr.findAll('td'):
            try:
                bs_contents.append( float( num_regex.sub('', td.contents[0]) ) )
            except ValueError:
                bs_contents.append( num_regex.sub('', td.contents[0]) ) 
        smry_data.append(bs_contents)
 
    return smry_data



def main(code, marketCode, tblName, cur):
	
	# url = "http://stocks.finance.yahoo.co.jp/stocks/detail/?code=%s.t" % (code)
	# Yahoo Finance では市場コードをつけなくても同じページが表示されるようなので、url表記を変える
	url = "http://profile.yahoo.co.jp/consolidate/%s" % (code)
	url_data = urllib2.urlopen(url).read().decode("euc-jp")
	# soup = BeautifulSoup(url_data)
	soup = get_soup(url_data)
	
	itemNames = []
	itemValues = []
	
	try :
		for kessan in soup.findAll('table', {'class' : 'yjMt'}):
			# 項目名の取得
			for koumoku in kessan.findAll('td', {'bgcolor':'#fafae7'}):
				itemNames.append(koumoku.contents[0])
				# print koumoku.contents[0]
			# 値の取得
			for val in kessan.findAll('td', {'align':'right'}):
				x = val.contents[0]
				# 桁区切りのコンマ、%などの表記は取り除く。
				# データがない箇所は'---'と入っているようなので、それも取り除く
				x = num_regex.sub('', hyphen_regex.sub('',x))
				itemValues.append(x)
			
		# 数字は当年、前年、前々年の３年分が入っている。１行に３年分あることから、
		# ３つ区切りにして数値を保存し直す
		val_tounen    = [x for (i, x) in enumerate(itemValues) if i%3==0]
		val_zennen    = [x for (i, x) in enumerate(itemValues) if i%3==1]
		val_zenzennen = [x for (i, x) in enumerate(itemValues) if i%3==2]
	
		# SQLに入れるために数字でないものをNULLにしたり、省いたりする
		val_tounen    = map((lambda x : getFloatValue(x) ), val_tounen)
		val_zennen    = map((lambda x : getFloatValue(x) ), val_zennen)
		val_zenzennen = map((lambda x : getFloatValue(x) ), val_zenzennen)
		
		# 必要なデータ項目だけを取り出して、SQL文を取得する
		sql_tounen = getInsertSQLToFinancialsConsolidate(val_tounen, "stockFinancialsConsolidate", code, marketCode, "2009")
		sql_zennen = getInsertSQLToFinancialsConsolidate(val_zennen, "stockFinancialsConsolidate", code, marketCode, "2008")
		sql_zenzennen = getInsertSQLToFinancialsConsolidate(val_zenzennen, "stockFinancialsConsolidate", code, marketCode, "2007")
		# print sql_tounen
		# print sql_zennen
		# print sql_zenzennen
		
		# インサートの実行。トランザクション処理を行う
		cur.execute(sql_tounen)
		cur.execute(sql_zennen)
		cur.execute(sql_zenzennen)
	
	except IndexError, e:
		#データがない場合、何もしない
		print "no financial data for stock code %s." % (code)
	except:
		pass
	
	
def getStockCodeList(date, cur):
	# con = stock_db.connect()
	# cur = con.cursor()
    # sql = """select distinct stockCode from stockPriceHistDaily 
    # where date='%s' and marketCode='1'; """ % (date)
	
	cur.execute(sql)
	stockCodeList = cur.fetchall()
	
	# cur.close()
	# con.close()
	
	return stockCodeList


def getInsertSQLToFinancials(data_list, tbl, stockCode, marketCode, year):
	"""
	取得した財務情報のリストから財務データテーブルに入れるための
	SQL文を返す。
	data_list : 財務情報の入ったリスト
	tbl       : データを入れるテーブル名
	year      : 財務情報の該当する年度。４桁で入力。
	"""
	try:
			# 必要な項目だけ取り出して変数に入れておく
		uriage     = data_list[3]                # 売上高
		eigyorieki = data_list[4]            # 営業利益
		keijorieki = data_list[5]            # 経常利益
		toukirieki = data_list[6]            # 当期利益
		eps        = data_list[7]            # 一株当り利益
		adjeps     = data_list[8]            # 調整済み一株当り利益
		dps        = data_list[9]            # 一株当り配当
		bps        = data_list[11]           # 一株当り純資産
		kabusu     = data_list[12]           # 発行済株式総数
		soushisan  = data_list[13]           # 総資産
		jikoshihon = data_list[14]           # 自己資本
		shihonkin  = data_list[15]           # 資本金
		debt       = data_list[16]           # 有利子負債
		kurikoshisoneki = data_list[17]      # 繰り越し損益
		capital_ratio   = data_list[18]      # 自己資本比率
		fukumieki  = data_list[19]           # 含み損益
		roa        = data_list[20]           # ROA 総資産利益率
		roe        = data_list[21]           # ROA 自己資本利益率
		riekiritsu = data_list[22]           # 総資産経常利益率
		
		sql = """INSERT INTO %s
		 (year, stockCode, marketCode, uriage, eigyorieki, keijorieki, toukirieki, 
		 eps, adjeps, dps, bps, kabusu, soushisan, jikoshihon, shihonkin, debt, kurikoshisonneki,
		 capital_ratio, fukumieki, roa, roe, riekiritsu)
		 VALUES('%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
		""" % (tbl, year, stockCode, marketCode, uriage, eigyorieki, keijorieki, toukirieki, 
			eps, adjeps, dps, bps, kabusu, soushisan, jikoshihon, shihonkin, debt, kurikoshisoneki,
			capital_ratio, fukumieki, roa, roe, riekiritsu)
		sql = re.sub("(\n|\t)","",sql)	# 改行文字が問題を起こすため取り除く
		# print sql
	except IndexError, e:
		# リストにデータが足りない場合は、何もしない
		print "not enough financial data for stock code %s." % (code)
	except NameError, e:
		# その他のエラーの場合は何もしない
		print "undefined variables used"
	except:
		print "unexpected error : ", sys.exc_info()[0] 
		
	return sql

def getInsertSQLToFinancialsConsolidate(data_list, tbl, stockCode, marketCode, year):
	"""
	取得した連結財務情報のリストから財務データテーブルに入れるための
	SQL文を返す。
	data_list : 財務情報の入ったリスト
	tbl       : データを入れるテーブル名
	year      : 財務情報の該当する年度。４桁で入力。
	"""
	try:
			# 必要な項目だけ取り出して変数に入れておく
		uriage     = data_list[3]            # 売上高
		eigyorieki = data_list[4]            # 営業利益
		keijorieki = data_list[5]            # 経常利益
		toukirieki = data_list[6]            # 当期利益
		eps        = data_list[7]            # 一株当り利益
		adjeps     = data_list[8]            # 調整済み一株当り利益
		bps        = data_list[9]            # 一株当り純資産
		soushisan  = data_list[10]           # 総資産
		jikoshihon = data_list[11]           # 自己資本
		shihonkin  = data_list[12]           # 資本金
		debt       = data_list[13]           # 有利子負債
		capital_ratio   = data_list[14]      # 自己資本比率
		fukumieki  = data_list[15]           # 含み損益
		roa        = data_list[16]           # ROA 総資産利益率
		roe        = data_list[17]           # ROA 自己資本利益率
		riekiritsu = data_list[18]           # 総資産経常利益率
		
		sql = """INSERT INTO %s
		 (year, stockCode, marketCode, uriage, eigyorieki, keijorieki, toukirieki, 
		 eps, adjeps, bps, soushisan, jikoshihon, shihonkin, debt, 
		 capital_ratio, fukumieki, roa, roe, riekiritsu)
		 VALUES('%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
		""" % (tbl, year, stockCode, marketCode, uriage, eigyorieki, keijorieki, toukirieki, 
			eps, adjeps, bps, soushisan, jikoshihon, shihonkin, debt,
			capital_ratio, fukumieki, roa, roe, riekiritsu)
		sql = re.sub("(\n|\t)","",sql)	# 改行文字が問題を起こすため取り除く
		# print sql
	except IndexError, e:
		# リストにデータが足りない場合は、何もしない
		print "not enough financial data for stock code %s." % (code)
	except NameError, e:
		# その他のエラーの場合は何もしない
		print "undefined variables used"
	except:
		print "unexpected error : ", sys.exc_info()[0] 
		
	return sql

#########################################
	
if __name__=='__main__':
    import stock_db
    import datetime

    # MSNから最新の銘柄リストを作る
    # cdlist = getStockCodeListFromMSN()
    # debug use 
    cdlist = ['1377','7203']

    # 損益計算書
    url_ps = "http://jp.moneycentral.msn.com/investor/invsub/results/statemnt.aspx?symbol=JP:%s"
    # 賃借対照表
    url_bs = url_ps + "&lstStatement=Balance&stmtView=Ann"
    # キャッシュフロー表
    url_cf = url_ps + "&lstStatement=CashFlow&stmtView=Ann"
    # １０年間の概括
    url_smry = url_ps + "&lstStatement=10YearSummary&stmtView=Ann"
           
    # print url_bs % '1377'
    # print url_cf % '1377'
    # print url_smry % '1377'

    for stockcd in cdlist:
        print "processing stock %s ..." % stockcd
        # データ取得
        data_ps = urllib2.urlopen(url_ps % stockcd).read()
        data_bs = urllib2.urlopen(url_bs % stockcd).read()
        data_cf = urllib2.urlopen(url_cf % stockcd).read()
        data_smry = urllib2.urlopen(url_smry % stockcd).read()

        # PSデータ
        print "---------- PS -----------"

        # 取得する財務データエリアの取得
        ps = get_soup(data_ps).find('table',{'class':'ftable'})
        # 財務データの年数を取る
        trr1 = ps.find('tr', {'class':'r1'})
        for num, td in enumerate(trr1.findAll('td')):
            if num > 0:
                print td.contents[0],
            
        print 

        for trft1 in ps.findAll('tr', {'class':'ft1'}):
            for td in trft1.findAll('td'):
                # 営業利益、など、項目名のエリアと、データが入っている列を区別する
                try:
                    print td.find('span').contents[0]
                except:
                    print num_regex.sub('', td.contents[0])

                # if td.findChild() != None:
                # print  td.findChildren()[0].contents[0],
                # else:
                # print num_regex.sub('', td.contents[0]),
            print 
                
        # BSデータ
        bs_arr = []
        print "---------- BS -----------"
        # 取得する財務データエリアの取得
        bs = get_soup(data_bs).find('table',{'class':'ftable'})
        # 財務データの年数を取る
        bs_year = []
        trr1 = bs.find('tr', {'class':'r1'})
        for num, td in enumerate(trr1.findAll('td')):
            if num > 0:
                bs_year.append(td.contents[0])
                print td.contents[0],
        print 
        bs_arr.append(bs_year)

        for trft1 in bs.findAll('tr', {'class':'ft1'}):
            for td in trft1.findAll('td'):
                # 営業利益、など、項目名のエリアと、データが入っている列を区別する
                if td.findChild() != None:
                    print  td.findChildren()[0].contents[0],
                else:
                    print num_regex.sub('', td.contents[0]),
            print 

        for trft2 in bs.findAll('tr', {'class':'ft2'}):
            for td in trft2.findAll('td'):
                # 営業利益、など、項目名のエリアと、データが入っている列を区別する
                if td.findChild() != None:
                    print  td.findChildren()[0].contents[0],
                else:
                    print num_regex.sub('', td.contents[0]),
            print 

        for trft3 in bs.findAll('tr', {'class':'ft3'}):
            for td in trft3.findAll('td'):
                # 営業利益、など、項目名のエリアと、データが入っている列を区別する
                if td.findChild() != None:
                    print  td.findChildren()[0].contents[0],
                else:
                    print num_regex.sub('', td.contents[0]),
            print 
        print "------------------"
        for num, trfd1 in enumerate(bs.findAll('tr', {'class':'fd1'})):
            # 長期投資、受取手形、その他固定資産だけを取り出し、投資その他資産を取得する
            if num >= 7 and num <=9:
                for td in trfd1.findAll('td'):
                    # 営業利益、など、項目名のエリアと、データが入っている列を区別する
                    if td.findChild() != None:
                        print  td.findChildren()[0].contents[0],
                    else:
                        print num_regex.sub('', td.contents[0]),
                print 

        print "------------------"
        # CF
        print "---------- CF ----------"
        # 取得する財務データエリアの取得
        cf = get_soup(data_cf).find('table',{'class':'ftable'})
        # 財務データの年数を取る
        trr1 = cf.find('tr', {'class':'r1'})
        for num, td in enumerate(trr1.findAll('td')):
            if num > 0:
                print td.contents[0],
        print 

        for trft1 in cf.findAll('tr', {'class':'ft1'}):
            for td in trft1.findAll('td'):
                # 営業利益、など、項目名のエリアと、データが入っている列を区別する
                if td.findChild() != None:
                    print  td.findChildren()[0].contents[0],
                else:
                    print num_regex.sub('', td.contents[0]),
            print 
            
        # 10-year summary 
        print "---------- 10-year summary ----------"
        # 取得する財務データエリアの取得
        # 損益計算書
        smry_ps = get_soup(data_smry).find('table',{'id':'INCS'})
        smry_bs = get_soup(data_smry).find('table',{'id':'BALS'})
        # 財務データの項目名を取る
        # PS
        # header
        trr1 = smry_ps.find('tr', {'class':'r1'})
        for td in trr1.findAll('td'):
            print td.contents[0],

        # data
        for tr in smry_ps.findAll('tr'):
            for td in tr.findAll('td'):
                print num_regex.sub('', td.contents[0]),
            print ""
        # BS
        trr1 = smry_bs.find('tr', {'class':'r1'})
        # header 
        for td in trr1.findAll('td'):
            print td.contents[0],

        for tr in smry_bs.findAll('tr'):
            for td in tr.findAll('td'):
                print num_regex.sub('', td.contents[0]),
            print 
        


        
    
	
    """
	con = stock_db.connect()
	cur = con.cursor()
	
	# 実行日の日付を取得
	today = datetime.date.today()
	lastTradingDate = getLastTradingDate(today.strftime('%Y-%m-%d'), cur)
	
	print "get stock code list from stockMaster as of %s" % lastTradingDate
	
	# stockCodeList = getStockCodeList(lastTradingDate, cur)
	stockCodeList = getStockAndMarketCodeList(lastTradingDate, cur)
	print "\nI am going to process %d stock\n" % len(stockCodeList)
	
	# stockFinancialsIndependentのデータを全て消す
	truncateTable(cur, "stockFinancialsConsolidate")
	
	# トランザクション処理開始
	cur.execute("START TRANSACTION;")
	for (cnt, code) in enumerate(stockCodeList):
		# 初めのインデックス指標は無視する
		if ( int(code[0]) > 1300 ):
		# if ( int(code[0]) > 6400 ):
			print "%s\tprocessing" % code[0]
			
			# main(code[0], "stockShihyo", cur)
			main(code[0], code[1], "stockFinancialsConsolidate", cur) # 全市場のデータを追加
			if (cnt+1) % 100 == 0:
				cur.execute("COMMIT;")
				cur.execute("START TRANSACTION;")
				print "processed %d stock record" % (cnt+1)
				 
	print "\ncommitting insert query..."
	cur.execute("COMMIT;")
	# cur.execute("ROLLBACK;")
	print "\ndata inserted to stockFinancialsConsolidate"
	
	cur.close()
	con.close()
    """
