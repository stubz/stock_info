# -*- coding: utf-8 -*-
import re, datetime, urllib2, sys
from BeautifulSoup import BeautifulSoup          # For processing HTML
from HTMLParser import HTMLParseError
sys.path.append('./lib/')
import stock_db

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

def main(code, marketCode, tblName, cur):
	
	# url = "http://stocks.finance.yahoo.co.jp/stocks/detail/?code=%s.t" % (code)
	# Yahoo Finance では市場コードをつけなくても同じページが表示されるようなので、url表記を変える
	url = "http://profile.yahoo.co.jp/independent/%s" % (code)
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
		sql_tounen = getInsertSQLToFinancials(val_tounen, "stockFinancialsIndependent", code, marketCode, "2009")
		sql_zennen = getInsertSQLToFinancials(val_zennen, "stockFinancialsIndependent", code, marketCode, "2008")
		sql_zenzennen = getInsertSQLToFinancials(val_zenzennen, "stockFinancialsIndependent", code, marketCode, "2007")
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
	
	
def getFloatValue(val):
	num = 0
	try:
		num = float(val)
	except ValueError:
		num = "\\N"
	return num

def getStockCodeList(date, cur):
	# con = stock_db.connect()
	# cur = con.cursor()
	sql = """select distinct stockCode from stockPriceHistDaily 
			where date='%s' and marketCode='1'; """ % (date)
	
	cur.execute(sql)
	stockCodeList = cur.fetchall()
	
	# cur.close()
	# con.close()
	
	return stockCodeList

def getStockAndMarketCodeList(date, cur):
	"""
	stockCode と marketCode のリスト（行列）を取得する
	"""
	sql = """select stockCode, marketCode from stockPriceHistDaily
			where date = '%s' """ % (date)
	cur.execute(sql)
	codelist = cur.fetchall()
	return codelist

def getLastTradingDate(today, cur):
	"""
	date で与えた日付の最も直近の取引日を取得する
	"""
	sql = "select date from calendarDaily where date <= '%s' order by date desc limit 1" % today
	cur.execute(sql)
	lastDate = cur.fetchone()
	return lastDate[0].strftime('%Y-%m-%d')

def truncateTable(cur, tbl):
	"""
	tbl で指定したテーブルを全部削除する
	"""	
	sql = "truncate table %s" % (tbl)
	cur.execute(sql)
	print "\n%s truncated.\n" % (tbl)
	
def truncateShihyoTable(cur):
	"""
	stockShihyo テーブルのデータを全部削除する。
	いったん消してから新しいデータを保存するようにする。
	"""	
	sql = "truncate table stockShihyo"
	cur.execute(sql)
	print "\nstockShihyo truncated.\n"

def truncateFinancialsIndependentTable(cur):
	"""
	stockFinancialsIndependent テーブルのデータを全部削除する。
	いったん消してから新しいデータを保存するようにする。
	"""	
	sql = "truncate table stockShihyo"
	cur.execute(sql)
	print "\nstockShihyo truncated.\n"

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
	
def get_soup( html ) :
	"""
	http://d.hatena.ne.jp/kumadeb/20090428
	<hoge alt=ほげ>
	のように日本語がダブルクォーテーションで囲まれていないとBeautifulSoupは
	HTMLParseErrorを返すらしく、それを回避するための関数（上記URL参照）
	<hoge alt="ほげ">
	というようにHTMLを修正する
	"""
	
	try:
		# HTMLソースをBeautifulSoupに渡す
		soup = BeautifulSoup(html)
		
	except HTMLParseError, e :
		# print "HTMLParseError raised"
		# エラーメッセージに"junk characters in start tag: "が含まれる場合
		e_words = "junk characters in start tag: "
		# print e_words
		if e.msg.find( e_words ) != -1 :
			# print "find(e_words)"
			"""
			エラーメッセージから"junk characters in start tag: "を取りのぞくと、
			エラーを引き起こしている文字列部分のみが取り出せます。
			BeautifulSoupの場合、受け取った文字列を内部でUnicode型に変換するため、
			取り出した文字列は u'xxxx' のような形になるので、一旦evalで評価して
			Unicode型のオブジェクトを生成し、改めて文字列型に直します。
			"""
			err_str = eval( e.msg.replace(e_words ,"" ))

			# print "error causing string \t%s" % (err_str)
			
			# 不完全なクオーテーションを削ります
			rpl_str = err_str.replace('"', '')
			rpl_str = rpl_str.replace("'", "")
			# '"ほげほげ">'のような形へ直します
			# rpl_str = "¥"%s¥">" % string.replace( rpt_str, ">", "" )
			# rpl_str = '"%s">' % rpl_str.replace(">", "" )
			# print "replaced string: \t%s" % (rpl_str)
			
			# エラーとなる文字列の中から日本語文字だけ取り出す
			# m_nihongo = nihongo_regex.search(rpl_str)
			nihongo_list = nihongo_regex.findall(rpl_str)
			# １文字ずつ分割されてリストに入れられるので、全文字をつなげる
			nihongo = ''.join(nihongo_list)
			# エラーとなる文字列全体のうち、日本語部分だけをダブルクォーテーションで囲んだ
			# 文字列に置換する
			rpl_str = rpl_str.replace(nihongo, '"'+nihongo+'"')
			# print "replaced new string: \t%s" % (rpl_str)
			# 最後にダウンロードしたHTML全体から、エラーが出る部分だけの文字列を置換する
			html = html.replace(err_str , rpl_str )
			# print html
			# get_soup関数を再帰的に呼び出します
			get_soup( html )
		#else :
			# その他のエラーが出た場合の対処を記述してください。
		#	raise e
		#	print "error1"
	#except Exception, e:
	#	# 想定外の例外の場合は再送出
	#	raise e
	#	print "error2"
	# print "end of function"
	return BeautifulSoup(html)
	
#########################################
	
if __name__=='__main__':
	import stock_db
	import datetime
	
	con = stock_db.connect()
	cur = con.cursor()
	
	# 実行日の日付を取得
	today = datetime.date.today()
	lastTradingDate = getLastTradingDate(today.strftime('%Y-%m-%d'), cur)
	
	print "get stock code list from stockMaster as of %s" % lastTradingDate
	
	# stockCodeList = getStockCodeList(lastTradingDate, cur)
	stockCodeList = getStockAndMarketCodeList(lastTradingDate, cur)
	print "\nI am going to process %d stock\n" % len(stockCodeList)

	"""
	if len(sys.argv)>2:
		code=sys.argv[1]
		marketCode=sys.argv[2]
		main(code, marketCode, 'stockShihyo')
	"""
	
	# stockFinancialsIndependentのデータを全て消す
	truncateTable(cur, "stockFinancialsIndependent")
	
	# トランザクション処理開始
	cur.execute("START TRANSACTION;")
	for (cnt, code) in enumerate(stockCodeList):
		# 初めのインデックス指標は無視する
		if ( int(code[0]) > 1300 ):
			print "%s\tprocessing" % code[0]
			# main(code[0], "stockShihyo", cur)
			main(code[0], code[1], "stockFinancialsIndependent", cur) # 全市場のデータを追加
			if (cnt+1) % 100 == 0:
				print "processed %d stock record" % (cnt+1)
				 
	print "\ncommitting insert query..."
	cur.execute("COMMIT;")
	print "\ndata inserted to stockFinancialsIndependent"
	
	cur.close()
	con.close()
