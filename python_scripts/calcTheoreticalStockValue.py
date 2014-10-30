# -*- coding: utf8 -*-

# 分析用に作った関数群
import stock
# DB接続用
import stock_db

def getCurrentRatioByIndustry(year):
    """
    業種別の流動比率をDBから取得して配列に入れる
    """
    sql = """
        select b.gyoshuCode, b.stockGyoshu, round(avg(a.ryudoshisan/ryudofusai), 1) as current_ratio
        from stockZaimuMSN a inner join stockMasterMSN b on a.stockCode = b.stockCode
        where a.ryudofusai > 0 and year = %s
        group by b.gyoshuCode, b.stockGyoshu
        """ % (year)

    con = stock_db.connect()
    con.query(sql)
    r = con.use_result()
    
    current_ratio = {}

    while(True):
        row = r.fetch_row(1,1)
        if not row: break
        current_ratio[row[0]['gyoshuCode']] = row[0]['current_ratio']

    con.close()
    return current_ratio

def getEquityRatioByIndustry(year):
    """
    業種別の平均自己資本比率をDBから取得して配列に入れる
    """
    sql = """
        select b.gyoshuCode, b.stockGyoshu, round(avg((a.asset-a.debt)/a.asset),3) as equity_ratio
        from stockZaimu10YearSmryMSN a inner join stockMasterMSN b on a.stockCode = b.stockCode
        where a.debt > 0 and truncate(a.yyyymm/100,0) = %s
        group by b.gyoshuCode, b.stockGyoshu;
        """ % (year)

    con = stock_db.connect()
    con.query(sql)
    r = con.use_result()
    
    equity_ratio = {}

    while(True):
        row = r.fetch_row(1,1)
        if not row: break
        equity_ratio[row[0]['gyoshuCode']] = row[0]['equity_ratio']

    con.close()
    return equity_ratio

def getExpectedReturnFromEquityRatio(equity_ratio):
    """
    自己資本比率から簡便的に期待リターンを計算する
    """
    expected_return = 0.0
    
    if equity_ratio == None:
        expected_return = 0.0
    if equity_ratio >= 0.5:
        expected_return = 0.09
    if equity_ratio >= 0.4 and equity_ratio < 0.5:
        expected_return = 0.08
    if equity_ratio >= 0.3 and equity_ratio < 0.4:
        expected_return = 0.07
    if equity_ratio >= 0.2 and equity_ratio < 0.3:
        expected_return = 0.06
    if equity_ratio < 0.2:
        expected_return = 0.05

    return expected_return

def getTheoreticalValuesForAllStock(cdlist, equity_ratio, current_ratio, tax_rate, year):
    """
    理論株価を計算してハッシュを返す
    """

    theoretical_values = {}

    for stockcd, gyoshucd in cdlist:
        # 自己資本比率から期待リターンを簡易的に決める
        expected_return = getExpectedReturnFromEquityRatio(equity_ratio[gyoshucd])
        # 各銘柄で財務データを取得
        try:
            zaimu = stock.getStockZaimuFromMSN(stockcd, year)
        except:
            continue

        # 投資その他資産を計算する
        # 長期投資＋受取手形＋その他固定資産計
        other_asset = int(zaimu['chokitoushi'])+int(zaimu['uketoritegata'])+int(zaimu['sonotakoteishisan'])

        # 理論価格を計算
        # 固定負債は負債合計ー流動負債で計算する
        stock_value = stock.getTheoreticalStockValueSimple(
                net_operating_income = zaimu['eigyorieki'],
                current_asset        = zaimu['ryudoshisan'],
                current_debt         = zaimu['ryudofusai'],
                other_asset          = other_asset,
                fixed_debt           = zaimu['fusai']-zaimu['ryudofusai'],
                shares               = zaimu['futsukabusu'],
                tax_rate             = tax_rate,
                current_ratio        = current_ratio[gyoshucd],
                expected_return      = expected_return)

        theoretical_values[stockcd] = stock_value
        # print "銘柄コード = %s\t理論価格 = %s" % (stockcd, stock_value)

    return theoretical_values
        

#################################################################################################
#################################################################################################
#################################################################################################

if __name__ == '__main__':

    # 理論株か計算に使う業種別流動比率、自己資本比率を計算するための設定
    year = 2009    # 使用するデータ年
    tax_rate = 0.4 # 法人税率

    # 業種別の流動比率をテーブルに入れる
    current_ratio = getCurrentRatioByIndustry(year)

    # 業種別の自己資本比率をテーブルに入れる
    equity_ratio= getEquityRatioByIndustry(year)

    # 銘柄リスト(stockCode, gyoshuCode)のタプルを作って、ループ
    cdlist = stock.getStockCodeListFromMSNMaster()

    # 銘柄リスト内の全銘柄について理論株価を計算し、ハッシュに保存する
    theoretical_values = getTheoreticalValuesForAllStock(cdlist, equity_ratio, current_ratio, tax_rate, year)

    # 
    check = {}
    check.setdefault(" ",0)
    check.setdefault("+",0)
    check.setdefault("-",0)
    check.setdefault("x",0)

    keys = theoretical_values.keys()
    keys.sort()

    # 書き込み
    with open("theoretical_result.txt", "w") as f:
        f.write("サイン\t銘柄コード\t理論価格\t期初価格\t期末価格\t変化率\n")

    for stockcd in keys:
        # 実際の株価を取得
        try:
            val_start = stock.getStockPriceFromDailyTable('2009-03-31', stockcd, '1')
            val_end   = stock.getStockPriceFromDailyTable('2010-01-29', stockcd, '1')
            # print stockcd, val_start, theoretical_values[stockcd]
            if theoretical_values[stockcd]>0 and val_start>0:
                # (i)  理論株価 < 期初株価 & 期初株価 < 期末株価
                # (ii) 理論株価 > 期初株価 & 期初株価 > 期末株価
                # 期初から上がったか下がったか
                chgrate = round(val_end/val_start-1,3)
                # 期初での理論株価乖離率
                kairi = round(theoretical_values[stockcd]/val_start-1, 3)
                sign = " "
                if chgrate > 0 and kairi > 0:
                    sign = "+"
                elif chgrate < 0 and kairi < 0:
                    sign = "-"
                # はずれた場合
                elif (chgrate < 0 and kairi > 0) or (chgrate>0 and kairi < 0):
                    sign = "x"

                # 的中した数と、その時の平均変化率を計算
                check[sign] += 1
                # print "%s | 銘柄コード:%s 理論価格=%s 期初価格=%s 期末価格=%s 変化率=%s" % (sign, stockcd, theoretical_values[stockcd], val_start, val_end, chgrate)
                with open("theoretical_result.txt", "a") as f:
                    res_string = "%s\t%s\t%s\t%s\t%s\t%s\n" % (sign, stockcd, theoretical_values[stockcd], val_start, val_end, chgrate)
                    f.write(res_string)
                # print "%s stockCode:%s theoretical=%s start=%s end=%s change_rate=%s" % (sign, stockcd, theoretical_values[stockcd], val_start, val_end, chgrate)
        except:
            continue

    print "上昇的中数:%d\t下降的中数:%d\tはずれれ:%d" % (check['+'], check['-'], check["x"])
