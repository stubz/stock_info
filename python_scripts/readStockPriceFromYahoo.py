# -*- coding: utf-8 -*-
import re, datetime, urllib2, sys
from BeautifulSoup import BeautifulSoup          # For processing HTML
sys.path.append('./lib/')
import stock_db

def main(code, marketCode, tblName, cur):
	numRegex = re.compile('\d+(\.*|\,*)\d+')
	# url = "http://stocks.finance.yahoo.co.jp/stocks/detail/?code=%s.t" % (code)
	# Yahoo Finance では市場コードをつけなくても同じページが表示されるようなので、url表記を変える
	url = "http://stocks.finance.yahoo.co.jp/stocks/detail/?code=%s" % (code)
	url_data = urllib2.urlopen(url).read()
	soup = BeautifulSoup(url_data)

	itemNames = []
	itemValues = []

	# 銘柄情報 詳細情報から板気配、参考指標のデータだけを取得する
	# css で <dd class='ymuiEditLink mar0'> で囲まれた行だけデータを取得

	shihyo = soup.findAll('dd', {'class' : 'ymuiEditLink mar0'})
	# 値は全て<strong>タグに囲まれている。
	for dd in shihyo:
		val = dd.strong.contents[0]
		# 桁区切りのコンマ、（実績）などの表記は取り除く
		val = re.sub("[^0-9\.\-]","",val)
		itemValues.append(val)

	# データを配列に入れていく。数字でなかった時のために、予め値に変換しておく
	# itemValues = map((lambda x : getFloatValue(x) ), itemValues)
	
	owarine       = getFloatValue(itemValues[0]) # 終値
	hajimene      = getFloatValue(itemValues[1]) # 始値
	takane        = getFloatValue(itemValues[2]) # 高値
	yasune        = getFloatValue(itemValues[3]) # 安値
	dekidaka      = getFloatValue(itemValues[4]) # 出来高
	baibaidaikin  = getFloatValue(itemValues[5]) # 売買代金
	# nehaba   = getFloatValue(itemValues[6]) # 値幅制限 100〜200などと入力されているため無視する
	jika     = getFloatValue(itemValues[7]) # 時価総額
	kabusu   = getFloatValue(itemValues[8]) # 発行済株式数 
	divRate  = getFloatValue(itemValues[9]) # 配当利回り（実績）
	dps      = getFloatValue(itemValues[10]) # １株配当（実績）
	per      = getFloatValue(itemValues[11]) # PER
	pbr      = getFloatValue(itemValues[12]) # PBR 
	eps      = getFloatValue(itemValues[13]) # EPS 
	bps      = getFloatValue(itemValues[14]) # BPS 
	saitei   = getFloatValue(itemValues[15]) # 最低購入代金
	tangen   = getFloatValue(itemValues[16]) # 単元部数
	# yearHigh = itemValues[17] # 年初来高値
	# yearLow  = itemValues[18] # 年初来安値
	kaizan   = getFloatValue(itemValues[19]) # 信用買残
	kaizanhi = getFloatValue(itemValues[20]) # 信用買残前週比
	taishaku = getFloatValue(itemValues[21]) # 貸借倍率
	urizan   = getFloatValue(itemValues[22]) # 信用売り残
	urizanhi = getFloatValue(itemValues[23]) # 信用売り残前週比
	
	"""
	for i in range(len(itemValues)):
		print "%s\t:%s" % (itemNames[i], itemValues[i])
	"""
    
	"""
	PER, PBR など株価によって変動するものは保存せず、決算期にのみ
	変わるような指標だけを保存する
	"""
	sql = """INSERT INTO %s
	(stockCode, marketCode, kabusu, dps, eps, bps, tangen)  
	VALUES('%s', '%s', %s, %s, %s, %s, %s);
	""" % (tblName, code, marketCode, kabusu, dps, eps, bps, tangen)

	sql = re.sub("(\n|\t)","",sql)
	# print sql
	# インサートの実行。トランザクション処理を行う
	cur.execute(sql)
	
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
	
def truncateShihyoTable(cur):
	"""
	stockShihyo テーブルのデータを全部削除する。
	いったん消してから新しいデータを保存するようにする。
	"""	
	sql = "truncate table stockShihyo"
	cur.execute(sql)
	print "\nstockShihyo truncated.\n"
	
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
	
	# stockShihyoのデータを全て消す
	truncateShihyoTable(cur)
	
	# トランザクション処理開始
	cur.execute("START TRANSACTION;")
	for (cnt, code) in enumerate(stockCodeList):
		# 初めのインデックス指標は無視する
		if ( int(code[0]) > 1300 ):
			# print "%s\tprocessing" % code[0]
			# main(code[0], "stockShihyo", cur)
			main(code[0], code[1], "stockShihyo", cur) # 全市場のデータを追加
			if (cnt+1) % 100 == 0:
				print "processed %d stock record" % (cnt+1)
				 
	print "\ncommitting insert query..."
	cur.execute("COMMIT;")
	print "\ndata inserted to stockShihyo"
	
	cur.close()
	con.close()