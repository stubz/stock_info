setwd("/Users/popopopo/myWork/stock_info/R_analysis")
library(RMySQL)
library(arules)
source("stock_db_connect.R")


m <- dbDriver("MySQL")
# 接続
con <- dbConnect(m, user="stock", password = "stock", 
				host="localhost", dbname = "stock_db")

test <- getStockChangeHistData(con, '7203', '1', '2009-07-06', '2009-07-10')


# 切断
dbDisconnect(con)

# 0/1のリストに変換する。上がったら１、下がったら０。変化なしの場合も０
apply(test,1,function(x){if(x>0){1}else{0}})


#

sql <- "select stockCode, changeDaily from stockPriceChangeDaily where marketCode = '1' and date >= '2009-07-06' and date <= '2009-07-10' order by stockCode, date desc;"

res <- dbSendQuery(con, sql)
test <- fetch(res, n=-1)
dbClearResult(res)



# ５日分のデータがある銘柄コードだけ抽出
stockList <- names(table(test$stockCode)==5)
test <- subset(test, stockCode %in% stockList)

# 0/1のリストに変換する。上がったら１、下がったら０。変化なしの場合も０
stockBinary <- sapply(test$changeDaily, function(x){if(x>0){1}else{0}})

# 銘柄コード別に横に五日分の値上がり、値下がりが付く行列を作る
stockData <- matrix(stockBinary, nrow=length(stockList), byrow=TRUE)
# 列名を変える
colnames(stockData) <- c("d1","d2","d3","d4","d5")
rownames(stockData) <- stockList

# --------------------- #
# 連関規則の分析を始める
# データは行列形式でないと変換ができないので注意
stock.trans <- as(stockData, "transactions")
summary(stock.trans)
# sizes : 1が何回現れるか、出現頻度別に集計(例えば2が300だったら、株価が２日上昇した銘柄が３００個あった事を意味する)

inspect(stock.trans)
# 各銘柄の値上がりの日付を見ている


# 何日目に値上がりしたか、出現確率を計算する
itemFrequency(stock.trans)

# １日前に値上がりした銘柄が一番多い
itemFrequencyPlot(stock.trans)

# 連関規則の構築
stock.rule <- apriori(stock.trans, parameter=list(maxlen=4, support=0.04, confidence=0.55, ext=TRUE))
# maxlen : １つの連関規則に含まれる最大項目数(ルールの長さ)
# support : 構築するサポートの下限(同時確率のこと)
# confidence : 構築する規則の信頼度の下限(条件付き確率のこと)
# ext = TRUE : 前提確率を示すlhs.supportの項も結果に含める

summary(stock.rule)

# 構築された規則の内容を見てみる
inspect(stock.rule)
# 






