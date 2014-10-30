# US市場で持っている銘柄のリスク管理プログラム
# ポートフォリオ全体でのリスクと、リターン、
# 銘柄ごとのリスクとリターン
# パフォーマンス分析
# の３つをトラックできるようにしたい


setwd("/Users/popopopo/myWork/stock_info/R_analysis")
library(fPortfolio)
library(fImport)

# Yahoo!からデータを取り込む
# 取得銘柄ティッカー
# 今持っている銘柄は
# AAPL : 5
# AMZN : 2
# CSCO : 10
# FXI : 40

# Adj. Close : Close price adjusted for dividends and splits.

# 

s1 <- yahooSeries("AAPL", from="2005-01-01")
s2 <- yahooSeries("AMZN", from="2005-01-01")
s3 <- yahooSeries("CSCO", from="2005-01-01")
s4 <- yahooSeries("FXI",  from="2005-01-01")

p1 <- s1[,6]
p2 <- s2[,6]
p3 <- s3[,6]
p4 <- s4[,6]

mypf <- cbind(p1,p2,p3,p4)
colnames(mypf) <- c("Apple","Amazon","Cisco","FXI")

mypf.ret <- returns(mypf)
summary(mypf.ret)
basicStats(mypf.ret)

round(cor(mypf.ret)*100,digits=4)

varRisk(mypf.ret*100,weights=c(5,2,10,40)/(5+2+10+40))
cvarRisk(mypf.ret*100,weights=c(5,2,10,40)/(5+2+10+40))

plot(mypf, plot.type="single",,col=1:4,xlab="Date", ylab="Adjusted Close Price")
hgrid()
legend("topleft", colnames(mypf), lty=c(1,1,1,1), col=1:4)

plot(mypf,xlab="Date", ylab="Adjusted Close Price", col="steelblue")

plot(mypf.ret, pch=19, cex=0.4, col="brown", xlab="Date", ylab="Adjusted Close Price", main="Progress of daily returns")
grid()

# 
seriesPlot(mypf[,1])
returnPlot(mypf[,1])
par(mfrow=c(2,2))
cumulatedPlot(mypf.ret)

histPlot(mypf.ret[,1])

######################################################################


start(IDX);end(IDX)

start(EPI);start(IDX);start(TOK);start(VNM);start(VWO)
max(start(EPI),start(IDX),start(TOK),start(VNM),start(VWO))

