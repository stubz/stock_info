# MySQLstock_dbに接続するための関数群

library(RMySQL)
library(fImport)
library(fPortfolio)


# 変数群
TBLpriceDaily <- "priceDaily"
TBLpriceWeekly <- "priceWeekly"
TBLpriceMonthly <- "priceMonthly"

TBLstockETFMaster <- "stockETFMaster"

stockDBConnect <- function()
{
	m <- dbDriver("MySQL")
	# 接続
	con <- dbConnect(m, user="stock", password = "stock", 
				host="localhost", dbname = "stock")
	return(con)
}


# データ取得


# データを取得して、RMetrics関数用にtimeSeries化する

getPriceDailyByCodeAll <- function(stockcd, marketcd)
{
	sql <- paste("select date, open, high, low, close, volume from ", TBLpriceDaily, 
			" WHERE stockcd = '", stockcd, "'",
			" AND marketcd = '", marketcd, "'", sep="")
	con <- stockDBConnect()
	res <- dbSendQuery(con, sql)
	dat <- fetch(res, n=-1) # n=-1 to retrieve all pending records
	dbClearResult(res)
	dbDisconnect(con)
	return(timeSeries(data=dat[,2:6], charvec=dat[,1], zone="Asia/Tokyo",FinCenter="Asia/Tokyo"))
}

getPriceDailyByCode <- function(stockcd, marketcd, startdate)
{
	sql <- paste("select date, open, high, low, close, volume from ", TBLpriceDaily, 
			" WHERE stockcd = '", stockcd, "'",
			" AND marketcd = '", marketcd, "'", 
			" AND date >= '", startdate, "'", sep="")
	con <- stockDBConnect()
	res <- dbSendQuery(con, sql)
	dat <- fetch(res, n=-1) # n=-1 to retrieve all pending records
	dbClearResult(res)
	dbDisconnect(con)
	return(timeSeries(data=dat[,2:6], charvec=dat[,1], zone="Asia/Tokyo",FinCenter="Asia/Tokyo"))
}



getPriceWeeklyByCodeAll <- function(stockcd, marketcd)
{
	sql <- paste("select date, open, high, low, close, volume from ", TBLpriceWeekly, 
			" WHERE stockcd = '", stockcd, "'",
			" AND marketcd = '", marketcd, "'", sep="")
	con <- stockDBConnect()
	res <- dbSendQuery(con, sql)
	dat <- fetch(res, n=-1) # n=-1 to retrieve all pending records
	dbClearResult(res)
	dbDisconnect(con)
	return(timeSeries(data=dat[,2:6], charvec=dat[,1]), zone="Asia/Tokyo",FinCenter="Asia/Tokyo")
}



# ETFの銘柄コードリストを取得
getETFCodeList <- function()
{
	sql <- paste("select stockcd, marketcd, stocknm from ", TBLstockETFMaster, sep="")
	con <- stockDBConnect()
	res <- dbSendQuery(con,sql)	
	dat <- fetch(res, n=-1) # n=-1 to retrieve all pending records
	dbClearResult(res)
	dbDisconnect(con)
	return(dat)
}


