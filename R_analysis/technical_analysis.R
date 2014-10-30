setwd("/Users/tatata/myWork/stock_info/R_analysis")
library(tseries)
library(RMySQL)
source("stock_db_connect.R")
source("technical_statistic_functions.R")

m <- dbDriver("MySQL")
# 接続
con <- dbConnect(m, user="stock", password = "stock", 
				host="localhost", dbname = "stock_db")

nikkei <- getStockData(connection = con, code = "1001", market.code=1, start="2006-01-04")
nikkei<-ts(nikkei$close, start=c(2006,1), frequency=248)
Ichimoku(x=nikkei)

# 移動平均線
Maverage(nikkei, 10, 30)
# 高島屋
takashimaya <- getStockData(con, "8233", 1, "2006-01-04")
takashimaya <- ts(takashimaya$close, start=c(2006,1), freq=248)
Maverage(takashimaya, 10, 30)

# RSI
Rsi(nikkei)
sumitomo<-getStockData(con, "8403", 1, "2006-01-04")
sumitomo<-ts(sumitomo$close, star=c(2006,1), freq=248)
Rsi(sumitomo)

# MACD
Macd(nikkei)
JRWest <- getStockData(con, "9021", 1, "2006-01-04")
JRWest <- ts(JRWest$close, start=c(2006,1), frequency=248)
Macd(JRWest, yrange=20000)

dbDisconnect(con)


