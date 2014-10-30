setwd("/Users/popopopo/myWork/stock_info/R_analysis")
source("stockDB.R")
library(fTrading)
library(fPortfolioBacktest)
# install.packages("fPortfolioBacktest", repos="http://R-Forge.R-project.org")

# このプログラムの目的
# 1. ポートフォリオのリスクと、個別銘柄のリスクを比較し、ポートフォリオでリスク分散ができているか確認する
# 2. 保有している銘柄の時価総額での資産配分が、どのように推移しているか確認する
#

# 目標資産配分
# 国内株式５０％、外国株式４０％、新興国１０％

# 1306 100 (topix)  1680 50 (MSCI-KOKUSAI) 1681 50 (MSCI EMERGING) 8282 100 (K's HOLDINGS)

stock1306 <- getPriceDailyByCode(stockcd='1306', marketcd='1', startdate='2008-01-01') # TOPIX ETF
stock1681 <- getPriceDailyByCode(stockcd='1681', marketcd='1', startdate='2008-01-01') # MSCI-Emerging
stock1680 <- getPriceDailyByCode(stockcd='1680', marketcd='1', startdate='2008-01-01') # MSCI-KOKUSAI
stock8282 <- getPriceDailyByCode(stockcd='8282', marketcd='1', startdate='2008-01-01') # ケーズホールディング
stock3092 <- getPriceDailyByCode(stockcd='3092', marketcd='3', startdate='2008-01-01') # スタートトゥデイ

# stock1306.close <- stock1306$close
# stock1681.close <- stock1681$close
# stock8282.close <- stock8282$close

stocks<-cbind(TOPIX=stock1306[,"close"],MSCI_KOKUSAI=stock1680[,"close"],
	MSCI_EME=stock1681[,"close"], K_HOLD=stock8282[,"close"], STARTTODAY=stock3092[,"close"])
holdings <- c(140,360,280,100,100)

# 2010-02-24以降にMSCI-EMERGING上場なので、それ以降のデータしかない
# スタートトゥデイは2011/1/27に株式分割１株->300.03株したので、２６日以前の株価を調整する。
stocks[rownames(stocks)<="2011-01-26","STARTTODAY"] <- floor(stocks[rownames(stocks)<="2011-01-26","STARTTODAY"]/300.03)

# by1 <- unique(timeLastDayInMonth(time(stocks), zone="Asia/Tokyo", FinCenter="Asia/Tokyo"))

# calculate portfolio value
ptfval <- timeSeries(stocks%*%holdings, zone="Asia/Tokyo",FinCenter="Asia/Tokyo", charvec=rownames(stock1306))
stocks <- timeSeries(stocks, zone="Asia/Tokyo",FinCenter="Asia/Tokyo", charvec=rownames(stock1306))

# add portfolio to the current timeSeries object
ptf <- timeSeries(cbind(stocks, port=ptfval), charvec=rownames(stock1306))
# head(ptf)

ptf.ret <- returns(ptf)
# head(ptf.ret)

round(colSds(ptf.ret)*100, 3)

apply(ptf.ret, 1, function(x) rollVar(x))
plot(sqrt(rollVar(ptf.ret[,1], n=100, unbiased=FALSE)))
plot(sqrt(rollVar(ptf.ret[,"port"])), main="Daily volatility movement", xlab="", ylab="" )

# それぞれの銘柄のボラティリティ
vol1 <- sqrt(rollVar(ptf.ret[,1], unbiased=FALSE))
vol2 <- sqrt(rollVar(ptf.ret[,2], unbiased=FALSE))
vol3 <- sqrt(rollVar(ptf.ret[,3], unbiased=FALSE))
vol4 <- sqrt(rollVar(ptf.ret[,4], unbiased=FALSE))
vol5 <- sqrt(rollVar(ptf.ret[,5], unbiased=FALSE))
vol6 <- sqrt(rollVar(ptf.ret[,6], unbiased=FALSE))

volat <- cbind(vol1,vol2,vol3,vol4,vol5,vol6)
colnames(volat) <- colnames(ptf)

plot(volat, col=1:6, main="Volatility of each stock")


## check correlation among holding stocks
n<-dim(ptf.ret)[1] # use only the last 200 days
round(cor(ptf.ret[(n-200):n,]), 2)
pairs(ptf.ret[(n-200):n,], pch=20)
# all positively correlated. The correlation is relatively low for MSCIKOKUSAI and MSCI_EMERGING





#####

# 資産配分比率の計算

(stocks.val <- stocks[800,] * holdings)
# apply(stocks,1,function(x)x*holdings)
stocks.val <- cbind(stocks[,1]*holdings[1], stocks[,2]*holdings[2], stocks[,3]*holdings[3],
		stocks[,4]*holdings[4],stocks[,5]*holdings[5])
colnames(stocks.val) <- colnames(stocks)[1:5]

stocks.ratio <- stocks.val/rowSums(stocks.val, na.rm=TRUE)
plot(stocks.ratio)

round(stocks.ratio[dim(stocks.ratio)[1],],3)*100

# 同じグラフに4つの線を引きたい
ts.plot(stocks.ratio, col=1:5, main="Ratio of stocks values")
legend("bottomleft", legend=colnames(stocks.val),col=1:5, lty=rep(1,5))


showClass("fPFOLIOBACKTEST")
defaultBacktest <- portfolioBacktest()
getWindowsFun(defaultBacktest)
getWindowsParams(defaultBacktest)

swxData <- 100*SWX.RET
swxBacktest <- portfolioBacktest()
setWindowsHorizon(swxBacktest) <- "24m"
equidistWindows(data = swxData, backtest = swxBacktest)

# (tangencyStrategy) : minimise Sharpe ratio, or min variance if such a portfolio does not exist



ptfSpec <- portfolioSpec()
ptfConstraints <- "LongOnly"
ptfBacktest <- portfolioBacktest()
setWindowsHorizon(ptfBacktest) <- "18m"
setSmootherLambda(ptfBacktest) <- "6m"




