# -*- coding: utf-8 -*-
"""
MSNファイナンスサイト
http://jp.moneycentral.msn.com
から各銘柄の財務諸表データを取得し、データベースに入れる
直近３年分のデータを取得できる。
データがEUCで保存されている前提（次期バージョンの改善点。簡単に文字コードの類推をするモジュールがあるらしい）

データ更新では１年分だけで十分だが、そこは毎回手で直す必要がある。
"""
import re, datetime, urllib2, sys
import dateutil.parser
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

# -------------------------- #
# -- データを取得するURL --- #
# -------------------------- #
url_MSN_finance = "http://jp.moneycentral.msn.com/investor/invsub/results/statemnt.aspx?symbol=JP:%s"
url_MSN_finance_PS  = url_MSN_finance + "&lstStatement=Income&stmtView=Qtr"
url_MSN_finance_BS  = url_MSN_finance + "&lstStatement=Balance&stmtView=Qtr"
url_MSN_finance_CF  = url_MSN_finance + "&lstStatement=CashFlow&stmtView=Qtr"
url_MSN_finance_10Y = url_MSN_finance + "&lstStatement=10YearSummary&stmtView=Qtr"


################################################################################

def insertZaimuData(stockcd, data):
    """
    データをDBに入れる。dataは縦に年数、横に項目が入ったもの。
    項目が保存された順番が非常に重要なので、getBSDataなどを使って作成したものを使う。
    また、これらに変更があった場合には、この関数にも影響があるので会わせて変更する事
    """ 

    con = stock_db.connect()

    sql_org = """INSERT INTO stockZaimuMSNQuarterly
            (stockcd, kessanbi, happyoubi, uriage, uriagesourieki, eigyorieki, zeikinmaejunrieki,
             zeihikigorieki, toukijunrieki, fusai, shihon, ryudoshisan, ryudofusai,
             shisan, shihonkei, chokitoushi, uketoritegata, sonotakoteishisan,
             futsukabusu, eigyocf, toushicf, zaimucf )
            VALUES ('%s','%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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

    try:
        con.commit()
        con.close()
    except:
        con.rollback()
        con.close()

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

    # 銘柄コードで指定した銘柄のデータをダウンロードして処理する
    data = urllib2.urlopen(url_MSN_finance_PS % stockcd).read()
        
    # データを保存するための配列。最終的には二次元の配列にする
    ps_data = []

    # 取得する財務データエリアの取得
    ps = get_soup(data).find('table',{'class':'ftable'})
    # データがない場合は無視する
    if ps == None:
        return ps_data

    # 決算日、決算発表日を取得する
    # 項目名に依存するので注意する
    for trfh in ps.findAll('tr', {'class':'fh'}):
        ps_date = []
        for td in trfh.findAll('td'):
            try:
                ps_date.append(td.contents[0])
            except IndexError:
                continue
            except:
                ps_date.append("")
        # 何もデータが入っていないようなタグがあるので、エラーチェックをかける
        if len(ps_date)>0 and (ps_date[0] == "決算年月日" or ps_date[0] == "決算発表日"):
            # 日付がyyyy/mm/ddの文字列になっているので、日付型に変換する。
            # 最初の要素に項目名が入っているが、日付以外のものが入っている場合は無視する
            for idx, val in enumerate(ps_date):
                try:
                    ps_date[idx] = dateutil.parser.parse(ps_date[idx], yearfirst=True).date()
                except ValueError:
                    # 日付以外の文字列が入っている場合
                    continue
            # 日付型に変換したものをデータとして追加する
            ps_data.append(ps_date)

    
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

    # 銘柄コードで指定した銘柄のデータをダウンロードして処理する
    data = urllib2.urlopen(url_MSN_finance_BS % stockcd).read()
        
    # データを保存するための配列。最終的には二次元の配列にする
    bs_data = []

    # 取得する財務データエリアの取得
    bs = get_soup(data).find('table',{'class':'ftable'})
    # データがない場合は無視する
    if bs == None:
        return bs_data

    # 決算日、決算発表日を取得する
    # 項目名に依存するので注意する
    for trfh in bs.findAll('tr', {'class':'fh'}):
        bs_date = []
        for td in trfh.findAll('td'):
            try:
                bs_date.append(td.contents[0])
            except IndexError:
                continue
            except:
                bs_date.append("")
        # 何もデータが入っていないようなタグがあるので、エラーチェックをかける
        if len(bs_date) > 0 and (bs_date[0] == "決算年月日" or bs_date[0] == "決算発表日"):
            # 日付がyyyy/mm/ddの文字列になっているので、日付型に変換する。
            # 最初の要素に項目名が入っているが、日付以外のものが入っている場合は無視する
            for idx, val in enumerate(bs_date):
                try:
                    bs_date[idx] = dateutil.parser.parse(bs_date[idx], yearfirst=True).date()
                except ValueError:
                    # 日付以外の文字列が入っている場合
                    continue
            # 日付型に変換したものをデータとして追加する
            bs_data.append(bs_date)

 
    # 財務データの年数を取る
    # 2009年第４四半期などと入っている箇所を取り出し
    """
    # とりあえず不要。決算日が入っているからそれにしておく
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
    """

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

    # 銘柄コードで指定した銘柄のデータをダウンロードして処理する
    data = urllib2.urlopen(url_MSN_finance_CF % stockcd).read()
        
    # データを保存するための配列。最終的には二次元の配列にする
    cf_data = []

    # 取得する財務データエリアの取得
    cf = get_soup(data).find('table',{'class':'ftable'})
    # データがない場合は無視する
    if cf == None:
        return cf_data

    # 決算日、決算発表日を取得する
    # 項目名に依存するので注意する
    for trfh in cf.findAll('tr', {'class':'fh'}):
        cf_date = []
        for td in trfh.findAll('td'):
            try:
                cf_date.append(td.contents[0])
            except IndexError:
                continue
            except:
                cf_date.append("")
        # 何もデータが入っていないようなタグがあるので、エラーチェックをかける
        if len(cf_date)>0 and (cf_date[0] == "決算年月日" or cf_date[0] == "決算発表日"):
            # 日付がyyyy/mm/ddの文字列になっているので、日付型に変換する。
            # 最初の要素に項目名が入っているが、日付以外のものが入っている場合は無視する
            for idx, val in enumerate(cf_date):
                try:
                    cf_date[idx] = dateutil.parser.parse(cf_date[idx], yearfirst=True).date()
                except ValueError:
                    # 日付以外の文字列が入っている場合
                    continue
            # 日付型に変換したものをデータとして追加する
            cf_data.append(cf_date)

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

#########################################
	
if __name__=='__main__':
    import stock_db
    import datetime

    con = stock_db.connect()
    cur = con.cursor()

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

        print "processing %s: %s ...." % (stockcd, stocklist['stocknm'])
        cnt += 1
        if cnt % 100 == 0:
            con.commit()
            print "inserted %d stocks ... " % cnt

        # PSのデータリストを取得
        data_ps = getPSData(stockcd)
        # BSのデータリストを取得
        data_bs = getBSData(stockcd)
        # CFのデータリストを取得
        data_cf = getCFData(stockcd)
        # 10年の概括のデータリストを取得
        # data_smry = get10YearSummaryData(stockcd)

        # データが全くない場合は無視する
        """
        if len(data_smry) == 0  or len(data_smry['ps']) <= 0 or len(data_smry['bs']) <= 0:
            print "no data for %s ..." % (stockcd)
            continue
        """

        # 財務データがない場合は無視する
        if len(data_ps) <= 0 or len(data_bs) <= 0 or len(data_cf) <= 0:
            continue

        # PS, BS, CFを縦につなげる
        # １行目は決算日、２行目は決算発表日が入っているので、BS, CFのデータからは取り除く
        data_bs.pop(0);data_bs.pop(0);
        data_cf.pop(0);data_cf.pop(0);
        # data_smry.pop(0)
        data = []

        for row in data_ps:
            data.append(row)
        for row in data_bs:
            data.append(row)
        for row in data_cf:
            data.append(row)

        # 行と列を入れ替える(Python Cookbook 4.8)
        data[:] = [[ r[col] for r in data] for col in range(len(data[0]))]

        # １行目は「売上高合計」など項目名が入っているだけなので、削除する
        data.pop(0)

        # ５年分のデータがあるので、sql 文を作って、データベースに挿入する
        insertZaimuData(stockcd, data)
        # insertZaimu10YearSummaryData(stockcd, data_smry, con)

    # con.commit()
    # インデックスを作る
    print "creating index..."
    # cur.execute("CREATE INDEX idxStockcd ON stockZaimu10YearSmryMSN (stockcd);")
    cur.execute("CREATE INDEX idxStockcd ON stockZaimuMSNQuarterly (stockcd);")
    cur.close()
    con.close()

