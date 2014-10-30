# MySQLstock_dbに接続するための関数群

# コード、市場コード、取得開始年月日を指定して
# 株価データを取得する。
getStockData<-function(connection, code, market.code, start)
{
	strQuery <- paste("SELECT * FROM orgkabuka WHERE code_c = '",
						code, "' AND mkt_code1 = ", market.code, 
						" AND date_c >= '", start, "'", sep = ""
					)
	res <- dbSendQuery(connection, strQuery)
	data <- fetch(res)
	dbClearResult(res)
	return(data)

}


getStockHistDailyData <- function(con, stockCode, marketCode, start, end)
{
	# 銘柄コード、市場コード、データ開始日、終了日を指定して時系列の過去データを取得する
	tbl <- "stockPriceHistDaily"
	
	sql <- paste("select open, high, low, close from ", tbl, 
			" where stockCode = ", "'", stockCode, "'",
			" and marketCode = ", "'", marketCode, "'", 
			" and date >= ", "'", start, "'",
			" and date <= ", "'", end, "'",
			" order by date desc;", sep=""
			)
	res <- dbSendQuery(con, sql)
	data <- fetch(res)
	dbClearResult(res)
	return(data)	
}

getStockChangeHistData <- function(con, stockCode, marketCode, startDate, endDate)
{
	# 銘柄コード、市場コード、データ開始日、終了日を指定して日次変化率の時系列の過去データを取得する
	tbl <- "stockPriceChangeDaily"
	
	sql <- paste("select changeDaily from ", tbl, 
			" where stockCode = ", "'", stockCode, "'",
			" and marketCode = ", "'", marketCode, "'", 
			" and date >= ", "'", startDate, "'",
			" and date <= ", "'", endDate, "'",
			" order by date desc;", sep=""
			)
	res <- dbSendQuery(con, sql)
	data <- fetch(res, n=-1)	# get all data by setting n = -1
	dbClearResult(res)
	return(data)
	
}
