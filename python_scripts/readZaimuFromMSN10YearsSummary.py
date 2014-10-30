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
from stockMSN import getStockCodeListFromMSN, getStockGyoshuListFromMSN, getStockCodeListFromMSNMaster
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

def insertZaimuData(stockcd, data, con):
    """
    データをDBに入れる。dataは縦に年数、横に項目が入ったもの。
    項目が保存された順番が非常に重要なので、getBSDataなどを使って作成したものを使う。
    また、これらに変更があった場合には、この関数にも影響があるので会わせて変更する事
    """ 

    sql_org = """INSERT INTO stockZaimuMSN 
            (stockcd, year, uriage, uriagesourieki, eigyorieki, zeikinmaejunrieki,
             zeihikigorieki, toukijunrieki, fusai, shihon, ryudoshisan, ryudofusai,
             shisan, shihonkei, chokitoushi, uketoritegata, sonotakoteishisan,
             futsukabusu, eigyocf, toushicf, zaimucf )
            VALUES ('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    for row in data:
        # ( stockcd, year, ... ) というタプルを作る。まずリストを作って、それをタプルに変換
        tmp = row[:]
        tmp.insert(0, stockcd)
        try:
            sql = sql_org % tuple(tmp)
            # print sql
            con.query(sql)
        except TypeError:
            # なぜかデータ追加でエラーが出たら無視する
            continue
        except:
            continue

def insertZaimu10YearSummaryData(stockcd, data, con):
    """
    10年間の統括データをデータベースに入れる
    """
    sql_org = """INSERT INTO stockZaimu10YearSmryMSN
            (stockcd, yyyymm, sales, ebit, depreciation,
             earnings, eps, taxrate, asset, debt, long_term_debt, shares)
            VALUES ('%s', %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """

    for i in range(len(data['ps'])):
        tmp = [stockcd]
        for val in data['ps'][i]:
            tmp.append(val)
        for val in data['bs'][i][1:]: # 最初の要素は年数なので、省く
            tmp.append(val)

        # print sql_org % tuple(tmp)
        try:
            sql = sql_org % tuple(tmp)
            con.query(sql)
        except TypeError:
            print "%s was not inserted ."
            continue
        except:
            print "%s was not inserted ."
            continue


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
    # データがない場合は無視する
    if ps == None:
        return ps_data
    # 財務データの年数を取る
    # 2009 2008 2007 等と入っている。初めの列はスペースだが、とりあえずそのまま読み込んでおく
    trr1 = ps.find('tr', {'class':'r1'})
    year_arr = []
    for num, td in enumerate(trr1.findAll('td')):
        try:
            year_arr.append( int(td.contents[0]) )
        except ValueError:
            year_arr.append(0)
        except IndexError:
            # 直近５年分のデータがない場合もあるので、その時は何もしない
            continue
        except:
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
            except IndexError:
                # 直近５年分のデータがない場合もあるので、その時は何もしない
                continue
            except:
                try:
                    # 数字に千区切りのコンマなどある場合があるので、それを取り除く
                    ps_contents.append( int( num_regex.sub('', td.contents[0] ) ) )
                except IndexError:
                    # 直近５年分のデータがない場合もあるので、その時は何もしない
                    continue
                except ValueError:
                    ps_contents.append(0)
                except:
                    continue

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
    # データがない場合は無視する
    if bs == None:
        return bs_data

    # 財務データの年数を取る
    # 2009 2008 2007 等と入っている。初めの列はスペースだが、とりあえずそのまま読み込んでおく
    trr1 = bs.find('tr', {'class':'r1'})
    year_arr = []
    for num, td in enumerate(trr1.findAll('td')):
        try:
            year_arr.append( int(td.contents[0]) )
        except ValueError:
            year_arr.append(0)
        except IndexError:
            # 直近５年分のデータがない場合もあるので、その時は何もしない
            continue
        except:
            continue
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
                except IndexError:
                    # 直近５年分のデータがない場合もあるので、その時は何もしない
                    continue
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
                except IndexError:
                    # 直近５年分のデータがない場合もあるので、その時は何もしない
                    continue
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
                except IndexError:
                    # 直近５年分のデータがない場合もあるので、その時は何もしない
                    continue
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
                    except IndexError:
                        # 直近５年分のデータがない場合もあるので、その時は何もしない
                        continue
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
                except IndexError:
                    # 直近５年分のデータがない場合もあるので、その時は何もしない
                    continue
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
    # データがない場合は無視する
    if cf == None:
        return cf_data
    # 財務データの年数を取る
    # 2009 2008 2007 等と入っている。初めの列はスペースだが、とりあえずそのまま読み込んでおく
    trr1 = cf.find('tr', {'class':'r1'})
    year_arr = []
    for td in trr1.findAll('td'):
        try:
            year_arr.append( int(td.contents[0]) )
        except IndexError:
            # 直近５年分のデータがない場合もあるので、その時は何もしない
            continue
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
                except IndexError:
                    # 直近５年分のデータがない場合もあるので、その時は何もしない
                    continue
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
    smry_data_ps = []
    smry_data_bs = []

    # 取得する財務データエリアの取得
    smry_ps = get_soup(data).find('table',{'id':'ctl00_ctl00_ctl00_HtmlBody_ctl00_HtmlBody_ctl00_HtmlBody_INCS'})
    smry_bs = get_soup(data).find('table',{'id':'ctl00_ctl00_ctl00_HtmlBody_ctl00_HtmlBody_ctl00_HtmlBody_BALS'})

    if smry_ps == None or smry_bs == None:
        return smry_data

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
            except IndexError:
                # 直近10年分のデータがない場合もあるので、その時は何もしない
                continue
            except ValueError:
                ps_contents.append( num_regex.sub('', td.contents[0]) ) 
        smry_data_ps.append(ps_contents)

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
            except IndexError:
                # 直近10年分のデータがない場合もあるので、その時は何もしない
                continue
            except ValueError:
                bs_contents.append( num_regex.sub('', td.contents[0]) ) 
        smry_data_bs.append(bs_contents)
 
    # return smry_data
    return {'ps':smry_data_ps, 'bs':smry_data_bs}

#########################################
	
if __name__=='__main__':
    import stock_db
    import datetime

    con = stock_db.connect()
    cur = con.cursor()

    # MSNから最新の銘柄リストを作る
    # cdlist = getStockCodeListFromMSN()
    # いったん作ったマスターテーブルから呼び込む
    cdlist = getStockCodeListFromMSNMaster()

    # debug use 
    # cdlist = [{'stockcd':'1377'}, {'stockcd':'7203'}]

    cnt = 0

    print "\n";print "-"*50
    print "\n各銘柄の財務データをダウンロードして、DBに入れる処理を開始します。\n"
    print "\n";print "-"*50

    for stocklist in cdlist:
        stockcd = stocklist['stockcd']

        # debug
        # 700 までは大丈夫だったので、それ以降やる
        # if stockcd < '3079':
        #            continue

        print "processing %s: %s ...." % (stockcd, stocklist['stocknm'])
        cnt += 1
        if cnt % 100 == 0:
            con.commit()
            print "inserted %d stocks ... " % cnt

        # 10年の概括のデータリストを取得
        data_smry = get10YearSummaryData(stockcd)

        # データが全くない場合は無視する
        if len(data_smry) == 0  or len(data_smry['ps']) <= 0 or len(data_smry['bs']) <= 0:
            print "no data for %s ..." % (stockcd)
            continue

        # sql 文を作って、データベースに挿入する
        insertZaimu10YearSummaryData(stockcd, data_smry, con)

    con.commit()
    # インデックスを作る
    print "creating index..."
    cur.execute("CREATE INDEX idxStockcd ON stockZaimu10YearSmryMSN (stockcd);")
    # cur.execute("CREATE INDEX idxStockcd ON stockZaimuMSN (stockcd);")
    cur.close()
    con.close()

